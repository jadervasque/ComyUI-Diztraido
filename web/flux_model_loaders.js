import { app } from "../../scripts/app.js";

const SUPPORTED_NODE_CLASSES = new Set([
    "DiztraidoLoadFlux2Models",
    "DiztraidoLoadFlux1Models",
    "DiztraidoLoadFlux2ModelsLoras",
]);

const LORA_NODE_CLASS = "DiztraidoLoadFlux2ModelsLoras";
const MAX_LORAS = 16;

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
    const vaeLora = node.widgets?.find((widget) => widget.name === "__sep_vae_lora");
    styleSeparatorWidget(modelClip);
    styleSeparatorWidget(clipVae);
    styleSeparatorWidget(vaeLora);
    node.setDirtyCanvas(true, true);
}

function clampCount(value) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
        return 0;
    }
    return Math.max(0, Math.min(MAX_LORAS, Math.trunc(parsed)));
}

function setWidgetVisibility(widget, visible) {
    if (!widget) {
        return;
    }
    widget.hidden = !visible;
    if (widget.inputEl) {
        widget.inputEl.style.display = visible ? "" : "none";
    }
}

function getLoraWidgetGroups(node) {
    const groups = [];
    for (let index = 1; index <= MAX_LORAS; index += 1) {
        groups.push([
            node.widgets?.find((widget) => widget.name === `lora_${index}`),
            node.widgets?.find((widget) => widget.name === `strength_model_${index}`),
            node.widgets?.find((widget) => widget.name === `strength_clip_${index}`),
        ]);
    }
    return groups;
}

function updateVisibleLoras(node, countWidget, groups) {
    const count = clampCount(countWidget?.value ?? 0);
    if (countWidget) {
        countWidget.value = count;
    }

    groups.forEach((group, index) => {
        for (const widget of group) {
            setWidgetVisibility(widget, index < count);
        }
    });
    node.setDirtyCanvas(true, true);
}

function createLoraControls(node, countWidget, groups) {
    const controls = document.createElement("div");
    Object.assign(controls.style, {
        display: "flex",
        gap: "6px",
        width: "100%",
        height: "100%",
        boxSizing: "border-box",
        paddingBottom: "8px",
    });

    for (const [label, delta] of [["Add LoRA", 1], ["Remove", -1]]) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = label;
        button.style.flex = "1";
        button.addEventListener("pointerdown", (event) => event.stopPropagation());
        button.addEventListener("click", (event) => {
            event.preventDefault();
            countWidget.value = clampCount((countWidget.value ?? 0) + delta);
            updateVisibleLoras(node, countWidget, groups);
        });
        controls.appendChild(button);
    }

    const widget = node.addDOMWidget(
        "lora_controls",
        "diztraido-lora-controls",
        controls,
        { serialize: false, hideOnZoom: false },
    );
    widget.computeSize = () => [0, 40];
}

function applyLoraControls(node) {
    const countWidget = node.widgets?.find((widget) => widget.name === "lora_count");
    if (!countWidget || node.__diztraidoLoraControlsReady) {
        return;
    }

    const groups = getLoraWidgetGroups(node);
    const originalCallback = countWidget.callback;
    countWidget.callback = function (value) {
        const result = originalCallback?.apply(this, arguments);
        countWidget.value = clampCount(value ?? countWidget.value);
        updateVisibleLoras(node, countWidget, groups);
        return result;
    };

    createLoraControls(node, countWidget, groups);
    updateVisibleLoras(node, countWidget, groups);
    node.__diztraidoLoraControlsReady = true;
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
            if (nodeData.name === LORA_NODE_CLASS) {
                applyLoraControls(this);
            }
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = originalOnConfigure?.apply(this, arguments);
            requestAnimationFrame(() => {
                applySeparators(this);
                if (nodeData.name === LORA_NODE_CLASS) {
                    updateVisibleLoras(
                        this,
                        this.widgets?.find((widget) => widget.name === "lora_count"),
                        getLoraWidgetGroups(this),
                    );
                }
            });
            return result;
        };
    },
});
