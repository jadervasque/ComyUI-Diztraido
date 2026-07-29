import { app } from "../../scripts/app.js";

const NODE_CLASSES = new Set([
    "DiztraidoResolutionSelector",
    "DiztraidoProcessingBundle",
]);
const CUSTOM_ASPECT_RATIO = "Custom";
const MIN_NODE_WIDTH = 180;

function roundTiesToEven(value) {
    const lower = Math.floor(value);
    const fraction = value - lower;
    if (fraction === 0.5) {
        return lower % 2 === 0 ? lower : lower + 1;
    }
    return Math.round(value);
}

function clampInteger(value, minimum, maximum, fallback) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
        return fallback;
    }
    return Math.max(minimum, Math.min(maximum, Math.trunc(parsed)));
}

function calculateResolution(aspectRatio, megapixels, multiple, width, height) {
    if (aspectRatio === CUSTOM_ASPECT_RATIO) {
        return [
            clampInteger(width, 8, 16384, 1024),
            clampInteger(height, 8, 16384, 1024),
        ];
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

function constrainWidgetInput(widget) {
    if (!widget?.inputEl) {
        return;
    }
    widget.inputEl.style.boxSizing = "border-box";
    widget.inputEl.style.maxWidth = "100%";
    widget.inputEl.style.minWidth = "0";
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

    if (widget.inputEl) {
        widget.inputEl.style.display = visible ? "" : "none";
        constrainWidgetInput(widget);
    }
}

function resizeNodeHeightToWidgets(node) {
    const computed = node.computeSize?.();
    if (!computed) {
        return;
    }

    const currentWidth = Number(node.size?.[0]) || Number(computed[0]) || MIN_NODE_WIDTH;
    const computedHeight = Number(computed[1]);
    const currentHeight = Number(node.size?.[1]) || 0;
    node.setSize?.([
        Math.max(MIN_NODE_WIDTH, currentWidth),
        Number.isFinite(computedHeight) ? computedHeight : currentHeight,
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

    const controlledWidgets = [
        aspectRatioWidget,
        megapixelsWidget,
        multipleWidget,
        widthWidget,
        heightWidget,
    ];

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
        const customMode = aspectRatioWidget.value === CUSTOM_ASPECT_RATIO;
        setWidgetVisible(megapixelsWidget, !customMode);
        setWidgetVisible(multipleWidget, !customMode);
        setWidgetVisible(widthWidget, customMode);
        setWidgetVisible(heightWidget, customMode);

        for (const widget of controlledWidgets) {
            constrainWidgetInput(widget);
        }

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

        resizeNodeHeightToWidgets(node);
        node.setDirtyCanvas?.(true, true);
    };

    for (const widget of controlledWidgets) {
        const originalCallback = widget.callback;
        widget.callback = function () {
            const result = originalCallback?.apply(this, arguments);
            refresh();
            return result;
        };
    }

    const originalOnResize = node.onResize;
    node.onResize = function () {
        const result = originalOnResize?.apply(this, arguments);
        for (const widget of controlledWidgets) {
            constrainWidgetInput(widget);
        }
        this.setDirtyCanvas?.(true, true);
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
