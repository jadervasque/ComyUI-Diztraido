import { app } from "../../scripts/app.js";

const NODE_CLASS = "DiztraidoResolutionSelector";

function roundTiesToEven(value) {
    const lower = Math.floor(value);
    const fraction = value - lower;
    if (fraction === 0.5) {
        return lower % 2 === 0 ? lower : lower + 1;
    }
    return Math.round(value);
}

function calculateResolution(aspectRatio, megapixels, multiple) {
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

function createResolutionPreview(node) {
    const aspectRatioWidget = node.widgets?.find((widget) => widget.name === "aspect_ratio");
    const megapixelsWidget = node.widgets?.find((widget) => widget.name === "megapixels");
    const multipleWidget = node.widgets?.find((widget) => widget.name === "multiple");
    if (!aspectRatioWidget || !megapixelsWidget || !multipleWidget || node.__diztraidoResolutionPreview) {
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
        const resolution = calculateResolution(
            aspectRatioWidget.value,
            megapixelsWidget.value,
            multipleWidget.value,
        );
        previewWidget.value = resolution
            ? `Output: ${resolution[0]} × ${resolution[1]} px`
            : "Output: unavailable";
        node.setDirtyCanvas?.(true, true);
    };

    for (const widget of [aspectRatioWidget, megapixelsWidget, multipleWidget]) {
        const originalCallback = widget.callback;
        widget.callback = function () {
            const result = originalCallback?.apply(this, arguments);
            refresh();
            return result;
        };
    }

    node.__diztraidoRefreshResolutionPreview = refresh;
    node.__diztraidoResolutionPreview = previewWidget;
    refresh();

    const computed = node.computeSize?.();
    if (computed) {
        node.setSize?.([
            Math.max(Number(node.size?.[0]) || 0, Number(computed[0]) || 0),
            Math.max(Number(node.size?.[1]) || 0, Number(computed[1]) || 0),
        ]);
    }
}

app.registerExtension({
    name: "diztraido.ResolutionSelector",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_CLASS) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            createResolutionPreview(this);
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = originalOnConfigure?.apply(this, arguments);
            requestAnimationFrame(() => this.__diztraidoRefreshResolutionPreview?.());
            return result;
        };
    },
});