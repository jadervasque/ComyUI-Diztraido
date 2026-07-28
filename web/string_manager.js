import { app } from "../../scripts/app.js";

const NODE_CLASS = "DiztraidoStringManager";
const MAX_FIELDS = 24;
const CUSTOM_ASPECT_RATIO = "Custom";

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

function clampInteger(value, minimum, maximum) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
        return minimum;
    }
    return Math.max(minimum, Math.min(maximum, Math.trunc(parsed)));
}

function resizeNode(node) {
    requestAnimationFrame(() => {
        const computed = node.computeSize?.();
        if (!computed) {
            return;
        }
        node.setSize?.([
            Math.max(520, Number(node.size?.[0]) || 0, Number(computed[0]) || 0),
            Number(computed[1]) || Number(node.size?.[1]) || 0,
        ]);
        node.setDirtyCanvas?.(true, true);
    });
}

function fieldWidgets(node, index) {
    const find = (name) => node.widgets?.find((widget) => widget.name === name);
    return {
        string: find(`string_${index}`),
        aspectRatio: find(`aspect_ratio_${index}`),
        megapixels: find(`megapixels_${index}`),
        multiple: find(`multiple_${index}`),
        width: find(`width_${index}`),
        height: find(`height_${index}`),
    };
}

function applyLabels(widgets, index) {
    if (widgets.string) widgets.string.label = `Prompt ${index}`;
    if (widgets.aspectRatio) widgets.aspectRatio.label = `Resolution ${index}`;
    if (widgets.megapixels) widgets.megapixels.label = `Megapixels ${index}`;
    if (widgets.multiple) widgets.multiple.label = `Multiple ${index}`;
    if (widgets.width) widgets.width.label = `Width ${index}`;
    if (widgets.height) widgets.height.label = `Height ${index}`;
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
        const widgets = fieldWidgets(node, index);
        applyLabels(widgets, index);
        groups.push(widgets);
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

        groups.forEach((widgets, zeroBasedIndex) => {
            const active = zeroBasedIndex < fieldCount;
            const custom = widgets.aspectRatio?.value === CUSTOM_ASPECT_RATIO;

            setWidgetVisible(widgets.string, active);
            setWidgetVisible(widgets.aspectRatio, active);
            setWidgetVisible(widgets.megapixels, active && !custom);
            setWidgetVisible(widgets.multiple, active && !custom);
            setWidgetVisible(widgets.width, active && custom);
            setWidgetVisible(widgets.height, active && custom);
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
        selectedWidget.value = clampInteger(
            selectedWidget.value,
            1,
            clampInteger(numFieldsWidget.value, 1, MAX_FIELDS),
        );
        node.setDirtyCanvas?.(true, true);
        return result;
    };

    groups.forEach((widgets) => {
        if (!widgets.aspectRatio) {
            return;
        }
        const originalCallback = widgets.aspectRatio.callback;
        widgets.aspectRatio.callback = function () {
            const result = originalCallback?.apply(this, arguments);
            refresh();
            return result;
        };
    });

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
