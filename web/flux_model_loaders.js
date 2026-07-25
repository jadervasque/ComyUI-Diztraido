import { app } from "../../scripts/app.js";

const LORA_NODE_CLASS = "DiztraidoLoadFlux2ModelsLoras";
const MAX_LORAS = 16;

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

    if (!Object.prototype.hasOwnProperty.call(widget, "__diztraidoOriginalComputeSize")) {
        widget.__diztraidoOriginalComputeSize = widget.computeSize;
    }

    widget.hidden = !visible;
    widget.computeSize = visible
        ? widget.__diztraidoOriginalComputeSize
        : () => [0, -4];

    if (widget.inputEl) {
        widget.inputEl.style.display = visible ? "" : "none";
    }
}

function fitNodeToContent(node) {
    if (!node || typeof node.computeSize !== "function" || typeof node.setSize !== "function") {
        return;
    }

    const computed = node.computeSize();
    const currentWidth = Number(node.size?.[0]) || 0;
    const computedWidth = Number(computed?.[0]) || currentWidth;
    const computedHeight = Math.max(0, Number(computed?.[1]) || 0);
    node.setSize([Math.max(currentWidth, computedWidth), computedHeight]);
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

    fitNodeToContent(node);
    requestAnimationFrame(() => fitNodeToContent(node));
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
        if (nodeData.name !== LORA_NODE_CLASS) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            applyLoraControls(this);
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = originalOnConfigure?.apply(this, arguments);
            requestAnimationFrame(() => {
                updateVisibleLoras(
                    this,
                    this.widgets?.find((widget) => widget.name === "lora_count"),
                    getLoraWidgetGroups(this),
                );
            });
            return result;
        };
    },
});
