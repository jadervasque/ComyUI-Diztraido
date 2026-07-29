import { app } from "../../scripts/app.js";

const NODE_CLASS = "DiztraidoReferenceChain";
const MAX_REFERENCES = 16;
const INPUT_PREFIX = "image_input_";
const INPUT_TYPE = "IMAGE";

function disableNativePreview(node) {
    node.imgs = null;
    node.images = null;
    node.imageIndex = null;
    node.preview = null;
}

function resolveInputImageUrl(imageName) {
    if (!imageName) {
        return "";
    }
    return `/view?filename=${encodeURIComponent(String(imageName))}&type=input`;
}

function clampCount(value) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
        return 0;
    }
    return Math.max(0, Math.min(MAX_REFERENCES, Math.trunc(parsed)));
}

function defer(callback, rounds = 1) {
    if (rounds <= 0) {
        callback();
        return;
    }
    requestAnimationFrame(() => defer(callback, rounds - 1));
}

function setWidgetVisibility(widget, visible) {
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

function getReferenceWidgets(node) {
    const widgets = [];
    for (let index = 1; index <= MAX_REFERENCES; index += 1) {
        widgets.push(node.widgets?.find((widget) => widget.name === `image_ref_${index}`));
    }
    return widgets;
}

function getDynamicReferenceInputs(node) {
    return (node.inputs ?? []).filter((input) => input.name?.startsWith(INPUT_PREFIX));
}

function rebuildReferenceInputs(node, countWidget, reset = false) {
    const target = clampCount(countWidget?.value ?? 0);
    if (countWidget) {
        countWidget.value = target;
    }

    let inputs = getDynamicReferenceInputs(node);
    if (reset) {
        for (const input of [...inputs].reverse()) {
            node.removeInput(node.inputs.indexOf(input));
        }
        inputs = [];
    }

    while (inputs.length > target) {
        const input = inputs.at(-1);
        node.removeInput(node.inputs.indexOf(input));
        inputs = getDynamicReferenceInputs(node);
    }

    const existing = new Set(inputs.map((input) => input.name));
    for (let index = 1; index <= target; index += 1) {
        const name = `${INPUT_PREFIX}${index}`;
        if (!existing.has(name)) {
            node.addInput(name, INPUT_TYPE);
        }
    }

    for (const input of getDynamicReferenceInputs(node)) {
        const index = Number(String(input.name).slice(INPUT_PREFIX.length));
        input.type = INPUT_TYPE;
        input.label = Number.isFinite(index) ? `Reference ${index} input` : input.name;
    }
}

function isDirectInputConnected(node, index) {
    const input = node.inputs?.find((item) => item.name === `${INPUT_PREFIX}${index}`);
    return input?.link != null;
}

function fitNodeToContent(node, minWidth = 360) {
    if (!node || typeof node.computeSize !== "function" || typeof node.setSize !== "function") {
        return;
    }
    const computed = node.computeSize();
    const currentWidth = Number(node.size?.[0]) || Number(computed?.[0]) || minWidth;
    const height = Math.max(0, Number(computed?.[1]) || 0);
    node.setSize([Math.max(minWidth, currentWidth), height]);
}

function createPreviewController(node) {
    const container = document.createElement("div");
    container.style.display = "none";
    container.style.gridTemplateColumns = "1fr";
    container.style.gap = "8px";
    container.style.width = "100%";
    container.style.height = "170px";
    container.style.maxHeight = "170px";
    container.style.overflowY = "hidden";
    container.style.padding = "2px";

    let visible = false;
    const widget = node.addDOMWidget(
        "references_preview",
        "diztraido-reference-preview",
        container,
        {
            serialize: false,
            hideOnZoom: false,
            getMinHeight: () => (visible ? 180 : 0),
            getMaxHeight: () => (visible ? 180 : 0),
            getHeight: () => (visible ? 180 : 0),
        },
    );
    widget.computeSize = (width) => (visible ? [Math.max(0, width), 180] : [0, -4]);

    const setVisible = (nextVisible) => {
        visible = Boolean(nextVisible);
        container.style.display = visible ? "grid" : "none";
        container.style.overflowY = visible ? "auto" : "hidden";
        if (!visible) {
            container.innerHTML = "";
        }
    };

    return { container, setVisible };
}

function renderReferencesPreview(node, preview, count, referenceWidgets) {
    const activeCount = clampCount(count);
    preview.container.innerHTML = "";
    let rendered = 0;

    for (let offset = 0; offset < activeCount; offset += 1) {
        const index = offset + 1;
        if (isDirectInputConnected(node, index)) {
            continue;
        }

        const imageName = referenceWidgets[offset]?.value;
        if (!imageName) {
            continue;
        }

        const card = document.createElement("div");
        card.style.display = "flex";
        card.style.flexDirection = "column";
        card.style.gap = "4px";

        const label = document.createElement("div");
        label.textContent = `Reference ${index}: ${String(imageName)}`;
        label.style.fontSize = "11px";
        label.style.whiteSpace = "nowrap";
        label.style.overflow = "hidden";
        label.style.textOverflow = "ellipsis";

        const image = document.createElement("img");
        image.src = resolveInputImageUrl(imageName);
        image.loading = "lazy";
        image.alt = `Reference ${index}`;
        image.style.display = "block";
        image.style.width = "100%";
        image.style.height = "140px";
        image.style.objectFit = "contain";
        image.style.border = "1px solid rgba(255,255,255,0.15)";
        image.style.borderRadius = "4px";
        image.style.background = "rgba(0, 0, 0, 0.18)";
        image.addEventListener("error", () => {
            card.remove();
            if (!preview.container.childElementCount) {
                preview.setVisible(false);
                fitNodeToContent(node);
            }
        });

        card.appendChild(label);
        card.appendChild(image);
        preview.container.appendChild(card);
        rendered += 1;
    }

    preview.setVisible(rendered > 0);
}

function createControls(node, countWidget, onChanged) {
    const addButton = node.addWidget("button", "Add Reference", null, () => {
        countWidget.value = clampCount((countWidget.value ?? 0) + 1);
        onChanged?.({ rebuildInputs: true });
    });
    addButton.options = { ...(addButton.options ?? {}), serialize: false };

    const removeButton = node.addWidget("button", "Remove", null, () => {
        countWidget.value = clampCount((countWidget.value ?? 0) - 1);
        onChanged?.({ rebuildInputs: true });
    });
    removeButton.options = { ...(removeButton.options ?? {}), serialize: false };

    return { addButton, removeButton };
}

function configureReferenceNode(node) {
    if (node.__diztraidoReferenceControlsReady) {
        return;
    }

    const countWidget = node.widgets?.find((widget) => widget.name === "reference_count");
    const referenceWidgets = getReferenceWidgets(node);
    if (!countWidget || !referenceWidgets.length) {
        return;
    }

    const preview = createPreviewController(node);
    const controls = createControls(node, countWidget, refresh);
    setWidgetVisibility(countWidget, false);

    function refresh({ rebuildInputs = false, resetInputs = false, fit = true } = {}) {
        const count = clampCount(countWidget.value);
        countWidget.value = count;

        if (rebuildInputs || resetInputs) {
            rebuildReferenceInputs(node, countWidget, resetInputs);
        }

        referenceWidgets.forEach((widget, offset) => {
            const index = offset + 1;
            const active = index <= count;
            const connected = active && isDirectInputConnected(node, index);
            if (!active && widget) {
                widget.value = "";
            }
            if (widget) {
                widget.disabled = connected;
                if (widget.inputEl) {
                    widget.inputEl.disabled = connected;
                }
            }
            setWidgetVisibility(widget, active && !connected);
        });

        setWidgetVisibility(controls.removeButton, count > 0);
        renderReferencesPreview(node, preview, count, referenceWidgets);
        disableNativePreview(node);

        if (fit) {
            fitNodeToContent(node);
        }
        node.setDirtyCanvas?.(true, true);
    }

    const originalCountCallback = countWidget.callback;
    countWidget.callback = function (value) {
        const result = originalCountCallback?.apply(this, arguments);
        countWidget.value = clampCount(value ?? countWidget.value);
        if (!node.__diztraidoConfiguringReferences) {
            refresh({ rebuildInputs: true });
        }
        return result;
    };

    referenceWidgets.forEach((widget) => {
        if (!widget) {
            return;
        }
        const originalCallback = widget.callback;
        widget.callback = function (value) {
            const result = originalCallback?.apply(this, arguments);
            if (value !== undefined) {
                widget.value = value;
            }
            refresh();
            return result;
        };
    });

    const originalConnectionsChange = node.onConnectionsChange;
    node.onConnectionsChange = function () {
        const result = originalConnectionsChange?.apply(this, arguments);
        requestAnimationFrame(() => refresh());
        return result;
    };

    const originalOnDrawBackground = node.onDrawBackground;
    node.onDrawBackground = function (ctx) {
        disableNativePreview(node);
        return originalOnDrawBackground?.call(this, ctx);
    };

    node.__diztraidoRefreshReferences = refresh;
    node.__diztraidoReferenceControlsReady = true;
    refresh({ resetInputs: true });
}

app.registerExtension({
    name: "diztraido.ReferenceChain",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_CLASS) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            configureReferenceNode(this);
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            this.__diztraidoConfiguringReferences = true;
            const result = originalOnConfigure?.apply(this, arguments);
            this.__diztraidoConfiguringReferences = false;
            defer(() => {
                configureReferenceNode(this);
                this.__diztraidoRefreshReferences?.({ rebuildInputs: true });
            }, 2);
            return result;
        };
    },
});
