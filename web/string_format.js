import { app } from "../../scripts/app.js";

const NODE_CLASS = "DiztraidoStringFormat";
const INPUT_PREFIX = "input_";
const INPUT_TYPE = "STRING,INT,FLOAT,BOOLEAN";
const MAX_INPUTS = 16;

function clampCount(value) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
        return 0;
    }
    return Math.max(0, Math.min(MAX_INPUTS, Math.trunc(parsed)));
}

function dynamicInputs(node) {
    return (node.inputs ?? []).filter((input) => input.name?.startsWith(INPUT_PREFIX));
}

function fitAfterRebuild(node, rebuild, reset = false) {
    const beforeHeight = Number(node.computeSize?.()?.[1]) || 0;
    const currentHeight = Number(node.size?.[1]) || beforeHeight;
    const extraHeight = reset ? 0 : Math.max(0, currentHeight - beforeHeight);
    const currentWidth = Number(node.size?.[0]) || 0;

    rebuild();

    const computed = node.computeSize?.() ?? node.size;
    const width = Math.max(currentWidth, Number(computed?.[0]) || currentWidth);
    const height = Math.max(0, Number(computed?.[1]) || 0) + extraHeight;
    node.setSize?.([width, height]);
    node.setDirtyCanvas?.(true, true);
}

function rebuildInputs(node, countWidget, reset = false) {
    const target = clampCount(countWidget.value);
    countWidget.value = target;

    fitAfterRebuild(node, () => {
        let inputs = dynamicInputs(node);
        if (reset) {
            for (const input of [...inputs].reverse()) {
                node.removeInput(node.inputs.indexOf(input));
            }
            inputs = [];
        }

        while (inputs.length > target) {
            const input = inputs.at(-1);
            const index = node.inputs.indexOf(input);
            node.removeInput(index);
            inputs = dynamicInputs(node);
        }

        const existing = new Set(inputs.map((input) => input.name));
        for (let index = 1; index <= target; index += 1) {
            const name = `${INPUT_PREFIX}${index}`;
            if (!existing.has(name)) {
                node.addInput(name, INPUT_TYPE);
            }
        }

        for (const input of dynamicInputs(node)) {
            input.type = INPUT_TYPE;
        }
    }, reset);
}

app.registerExtension({
    name: "diztraido.StringFormat",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_CLASS) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            const countWidget = this.widgets?.find((widget) => widget.name === "input_count");
            if (!countWidget) {
                return result;
            }

            const node = this;
            const originalCallback = countWidget.callback;
            countWidget.callback = function (value) {
                const callbackResult = originalCallback?.apply(this, arguments);
                countWidget.value = clampCount(value ?? countWidget.value);
                if (!node.__diztraidoConfiguringStringFormat) {
                    rebuildInputs(node, countWidget);
                }
                return callbackResult;
            };

            node.__diztraidoRebuildStringInputs = (reset = false) => {
                rebuildInputs(node, countWidget, reset);
            };
            node.__diztraidoRebuildStringInputs(true);
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            this.__diztraidoConfiguringStringFormat = true;
            const result = originalOnConfigure?.apply(this, arguments);
            this.__diztraidoConfiguringStringFormat = false;
            requestAnimationFrame(() => this.__diztraidoRebuildStringInputs?.());
            return result;
        };
    },
});