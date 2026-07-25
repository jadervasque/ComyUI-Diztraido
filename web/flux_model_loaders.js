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

function createLayoutController(node) {
    let extraHeight = 0;
    let isApplyingSize = false;

    const measureContent = () => {
        const computed = node.computeSize();
        return {
            width: Math.max(0, Number(computed?.[0]) || 0),
            height: Math.max(0, Number(computed?.[1]) || 0),
        };
    };

    const captureExtraHeight = () => {
        if (isApplyingSize) {
            return;
        }
        const content = measureContent();
        const currentHeight = Number(node.size?.[1]) || content.height;
        extraHeight = Math.max(0, currentHeight - content.height);
    };

    const fit = () => {
        const content = measureContent();
        const currentWidth = Number(node.size?.[0]) || content.width;
        isApplyingSize = true;
        node.setSize([
            Math.max(currentWidth, content.width),
            content.height + extraHeight,
        ]);
        isApplyingSize = false;
    };

    const resetAndFit = () => {
        extraHeight = 0;
        fit();
    };

    const originalOnResize = node.onResize;
    node.onResize = function () {
        const result = originalOnResize?.apply(this, arguments);
        captureExtraHeight();
        return result;
    };

    return { captureExtraHeight, fit, resetAndFit };
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

function updateVisibleLoras(node, countWidget, groups, layout, mode = "preserve") {
    const count = clampCount(countWidget?.value ?? 0);
    if (countWidget) {
        countWidget.value = count;
    }

    if (mode === "preserve") {
        layout.captureExtraHeight();
    }

    groups.forEach((group, index) => {
        for (const widget of group) {
            setWidgetVisibility(widget, index < count);
        }
    });

    if (mode === "restore") {
        layout.captureExtraHeight();
    }

    if (mode === "reset") {
        layout.resetAndFit();
    } else {
        layout.fit();
    }
    node.setDirtyCanvas(true, true);
}

function createLoraControls(node, countWidget, groups, layout) {
    for (const [label, delta] of [["Add LoRA", 1], ["Remove", -1]]) {
        const button = node.addWidget("button", label, null, () => {
            countWidget.value = clampCount((countWidget.value ?? 0) + delta);
            updateVisibleLoras(node, countWidget, groups, layout);
        });
        button.options = { ...(button.options ?? {}), serialize: false };
    }
}

function applyLoraControls(node) {
    const countWidget = node.widgets?.find((widget) => widget.name === "lora_count");
    if (!countWidget || node.__diztraidoLoraControlsReady) {
        return;
    }

    const groups = getLoraWidgetGroups(node);
    const layout = createLayoutController(node);
    const originalCallback = countWidget.callback;
    countWidget.callback = function (value) {
        const result = originalCallback?.apply(this, arguments);
        countWidget.value = clampCount(value ?? countWidget.value);
        if (!node.__diztraidoIsConfiguringLoras) {
            updateVisibleLoras(node, countWidget, groups, layout);
        }
        return result;
    };

    createLoraControls(node, countWidget, groups, layout);
    updateVisibleLoras(node, countWidget, groups, layout, "reset");
    node.__diztraidoLoraLayout = layout;
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
            this.__diztraidoIsConfiguringLoras = true;
            const result = originalOnConfigure?.apply(this, arguments);
            this.__diztraidoIsConfiguringLoras = false;
            requestAnimationFrame(() => {
                updateVisibleLoras(
                    this,
                    this.widgets?.find((widget) => widget.name === "lora_count"),
                    getLoraWidgetGroups(this),
                    this.__diztraidoLoraLayout,
                    "restore",
                );
            });
            return result;
        };
    },
});
