import { app } from "../../scripts/app.js";

const NODE_CLASSES = new Set([
    "DiztraidoResolutionSelector",
    "DiztraidoProcessingBundle",
]);
const CUSTOM_ASPECT_RATIO = "Custom";

function roundTiesToEven(value) {
    const lower = Math.floor(value);
    const fraction = value - lower;
    if (fraction === 0.5) {
        return lower % 2 === 0 ? lower : lower + 1;
    }
    return Math.round(value);
}

function calculateResolution(aspectRatio, megapixels, multiple, width, height) {
    if (aspectRatio === CUSTOM_ASPECT_RATIO) {
        const customWidth = Number(width);
        const customHeight = Number(height);
        if (!Number.isFinite(customWidth) || !Number.isFinite(customHeight)) {
            return null;
        }
        return [Math.trunc(customWidth), Math.trunc(customHeight)];
    }

    const match = String(aspectRatio ?? "").match(/^(\d+):(\d+)/);
    const targetMegapixels = Number(megapixels);
    const targetMultiple = Number(multiple);
    if (!match || !Number.isFinite(targetMegapixels) || !Number.isFinite(targetMultiple) || targetMultiple <= 0) {
        return null;
    }

    const widthRatio = Number(match[1]);
    const heightRatio = Number(match[2]);
    const totalPixels = targetMegapixels * 1024 * 1024;
    const scale = Math.sqrt(totalPixels / (widthRatio * heightRatio));
    return [
        roundTiesToEven(widthRatio * scale / targetMultiple) * targetMultiple,
        roundTiesToEven(heightRatio * scale / targetMultiple) * targetMultiple,
    ];
}

function setWidgetVisible(widget, visible) {
    if (!widget) {
        return;
    }

    if (!widget.__diztraidoVisibilityState) {
        widget.__diztraidoVisibilityState = {
            type: widget.type,
            computeSize: widget.computeSize,
        };
    }

    widget.hidden = !visible;
    if (visible) {
        widget.type = widget.__diztraidoVisibilityState.type;
        widget.computeSize = widget.__diztraidoVisibilityState.computeSize;
    } else {
        widget.type = "diztraido-hidden-widget";
        widget.computeSize = () => [0, -4];
    }
}

function resizeNodeToWidgets(node) {
    const computed = node.computeSize?.();
    if (!computed) {
        return;
    }
    node.setSize?.([
        Math.max(Number(node.size?.[0]) || 0, Number(computed[0]) || 0),
        Number(computed[1]) || Number(node.size?.[1]) || 0,
    ]);
}

function configureResolutionWidgets(node) {
    if (node.__diztraidoResolutionConfigured) {
        return;
    }

    const aspectRatioWidget = node.widgets?.find((widget) => widget.name === "aspect_ratio");
    const megapixelsWidget = node.widgets?.find((widget) => widget.name === "megapixels");
    const multipleWidget = node.widgets?.find((widget) => widget.name === "multiple");
    const widthWidget = node.widgets?.find((widget) => widget.name === "width");
    const heightWidget = node.widgets?.find((widget) => widget.name === "height");
    if (!aspectRatioWidget || !megapixelsWidget || !multipleWidget || !widthWidget || !heightWidget) {
        return;
    }

    const previewWidget = node.addCustomWidget({
        name: "resolution_preview",
        type: "diztraido-resolution-preview",
        value: "Output: unavailable",
        options: { serialize: false },
        computeSize: () => [0, 30],
        draw(ctx, currentNode, width, y, height) {
            ctx.save();
            ctx.fillStyle = "#ddd";
            ctx.font = "600 13px sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(this.value, width / 2, y + height / 2);
            ctx.restore();
        },
        serialize: false,
    });

    const refresh = () => {
        const resolutionInput = node.inputs?.find((input) => input.name === "resolution");
        const connectedResolution = resolutionInput?.link != null;
        const customMode = aspectRatioWidget.value === CUSTOM_ASPECT_RATIO;

        setWidgetVisible(aspectRatioWidget, !connectedResolution);
        setWidgetVisible(megapixelsWidget, !connectedResolution && !customMode);
        setWidgetVisible(multipleWidget, !connectedResolution && !customMode);
        setWidgetVisible(widthWidget, !connectedResolution && customMode);
        setWidgetVisible(heightWidget, !connectedResolution && customMode);

        if (connectedResolution) {
            previewWidget.value = "Output: connected resolution";
        } else {
            const resolution = calculateResolution(
                aspectRatioWidget.value,
                megapixelsWidget.value,
                multipleWidget.value,
                widthWidget.value,
                heightWidget.value,
            );
            previewWidget.value = resolution
                ? `Output: ${resolution[0]} × ${resolution[1]} px`
                : "Output: unavailable";
        }

        resizeNodeToWidgets(node);
        node.setDirtyCanvas?.(true, true);
    };

    for (const widget of [aspectRatioWidget, megapixelsWidget, multipleWidget, widthWidget, heightWidget]) {
        const originalCallback = widget.callback;
        widget.callback = function () {
            const result = originalCallback?.apply(this, arguments);
            refresh();
            return result;
        };
    }

    const originalConnectionsChange = node.onConnectionsChange;
    node.onConnectionsChange = function () {
        const result = originalConnectionsChange?.apply(this, arguments);
        requestAnimationFrame(refresh);
        return result;
    };

    node.__diztraidoRefreshResolutionPreview = refresh;
    node.__diztraidoResolutionConfigured = true;
    refresh();
}

app.registerExtension({
    name: "diztraido.ResolutionSelector",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (!NODE_CLASSES.has(nodeData.name)) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            configureResolutionWidgets(this);
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = originalOnConfigure?.apply(this, arguments);
            requestAnimationFrame(() => {
                configureResolutionWidgets(this);
                this.__diztraidoRefreshResolutionPreview?.();
            });
            return result;
        };
    },
});
