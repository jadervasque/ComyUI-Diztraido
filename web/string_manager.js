import { app } from "../../scripts/app.js";

const NODE_CLASS = "DiztraidoStringManager";
const MAX_FIELDS = 24;

function clampInteger(value, minimum, maximum) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
        return minimum;
    }
    return Math.max(minimum, Math.min(maximum, Math.trunc(parsed)));
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
    }
}

function resizeNode(node) {
    requestAnimationFrame(() => {
        const computed = node.computeSize?.();
        if (!computed) {
            return;
        }

        const currentWidth = Number(node.size?.[0]) || 0;
        node.setSize?.([
            Math.max(520, currentWidth, Number(computed[0]) || 0),
            Number(computed[1]) || Number(node.size?.[1]) || 0,
        ]);
        node.setDirtyCanvas?.(true, true);
    });
}

function configureStringManager(node) {
    if (node.__diztraidoStringManagerConfigured) {
        return;
    }

    const numFieldsWidget = node.widgets?.find((widget) => widget.name === "num_fields");
    const selectedWidget = node.widgets?.find((widget) => widget.name === "selected_string");
    if (!numFieldsWidget || !selectedWidget) {
        return;
    }

    numFieldsWidget.label = "Number of fields";
    selectedWidget.label = "Selected string";

    const groups = [];
    for (let index = 1; index <= MAX_FIELDS; index += 1) {
        const promptWidget = node.widgets?.find((widget) => widget.name === `string_${index}`);
        const aspectRatioWidget = node.widgets?.find(
            (widget) => widget.name === `aspect_ratio_${index}`,
        );

        if (promptWidget) {
            promptWidget.label = `Prompt ${index}`;
        }
        if (aspectRatioWidget) {
            aspectRatioWidget.label = `Aspect ratio ${index}`;
        }

        groups.push({ promptWidget, aspectRatioWidget });
    }

    const refresh = () => {
        const fieldCount = clampInteger(numFieldsWidget.value, 1, MAX_FIELDS);
        numFieldsWidget.value = fieldCount;

        selectedWidget.options = {
            ...(selectedWidget.options ?? {}),
            min: 1,
            max: fieldCount,
            step: 1,
        };
        selectedWidget.value = clampInteger(selectedWidget.value, 1, fieldCount);

        groups.forEach((group, zeroBasedIndex) => {
            const visible = zeroBasedIndex < fieldCount;
            setWidgetVisible(group.promptWidget, visible);
            setWidgetVisible(group.aspectRatioWidget, visible);
        });

        resizeNode(node);
    };

    const originalNumFieldsCallback = numFieldsWidget.callback;
    numFieldsWidget.callback = function () {
        const result = originalNumFieldsCallback?.apply(this, arguments);
        refresh();
        return result;
    };

    const originalSelectedCallback = selectedWidget.callback;
    selectedWidget.callback = function () {
        const result = originalSelectedCallback?.apply(this, arguments);
        const fieldCount = clampInteger(numFieldsWidget.value, 1, MAX_FIELDS);
        selectedWidget.value = clampInteger(selectedWidget.value, 1, fieldCount);
        node.setDirtyCanvas?.(true, true);
        return result;
    };

    node.__diztraidoRefreshStringManager = refresh;
    node.__diztraidoStringManagerConfigured = true;
    refresh();
}

app.registerExtension({
    name: "diztraido.StringManager",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_CLASS) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            configureStringManager(this);
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = originalOnConfigure?.apply(this, arguments);
            requestAnimationFrame(() => {
                configureStringManager(this);
                this.__diztraidoRefreshStringManager?.();
            });
            return result;
        };
    },
});
