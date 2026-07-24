import { app } from "../../scripts/app.js";

const SUPPORTED_NODE_CLASSES = new Set([
    "DiztraidoLoadFlux2Models",
    "DiztraidoLoadFlux1Models",
]);

function styleSeparatorWidget(widget) {
    if (!widget) {
        return;
    }

    widget.label = "";
    widget.value = "";

    const input = widget.inputEl;
    if (!input) {
        return;
    }

    input.readOnly = true;
    input.tabIndex = -1;
    input.value = "";
    input.style.pointerEvents = "none";
    input.style.cursor = "default";
    input.style.height = "8px";
    input.style.minHeight = "8px";
    input.style.padding = "0";
    input.style.margin = "4px 0";
    input.style.border = "0";
    input.style.borderTop = "1px solid rgba(255, 255, 255, 0.18)";
    input.style.borderRadius = "0";
    input.style.background = "transparent";
    input.style.color = "transparent";

    widget.computeSize = () => [0, 12];
}

function applySeparators(node) {
    const modelClip = node.widgets?.find((widget) => widget.name === "__sep_model_clip");
    const clipVae = node.widgets?.find((widget) => widget.name === "__sep_clip_vae");
    styleSeparatorWidget(modelClip);
    styleSeparatorWidget(clipVae);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "diztraido.FluxModelLoaders",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (!SUPPORTED_NODE_CLASSES.has(nodeData.name)) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            applySeparators(this);
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = originalOnConfigure?.apply(this, arguments);
            requestAnimationFrame(() => applySeparators(this));
            return result;
        };
    },
});
