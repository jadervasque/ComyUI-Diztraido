import { app } from "../../scripts/app.js";

const NODE_CLASS = "DiztraidoReferenceChain";
const MAX_REFERENCES = 16;

function disableNativePreview(node) {
    // ComfyUI pode manter preview interno do primeiro widget de imagem.
    // Limpamos estados conhecidos para evitar renderizacao desse bloco no rodape do no.
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

function setWidgetVisibility(widget, visible) {
    if (!widget) {
        return;
    }

    widget.hidden = !visible;

    if (widget.inputEl) {
        widget.inputEl.style.display = visible ? "" : "none";
    }
}

function getReferenceWidgets(node) {
    const references = [];
    for (let index = 1; index <= MAX_REFERENCES; index += 1) {
        references.push(node.widgets?.find((widget) => widget.name === `image_ref_${index}`));
    }
    return references;
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

function updateVisibleReferences(node, countWidget, referenceWidgets) {
    const count = clampCount(countWidget?.value ?? 0);
    if (countWidget) {
        countWidget.value = count;
    }

    referenceWidgets.forEach((widget, index) => {
        setWidgetVisibility(widget, index < count);
    });

    disableNativePreview(node);
    node.setDirtyCanvas(true, true);
}

function renderReferencesPreview(previewRoot, count, referenceWidgets) {
    if (!previewRoot) {
        return;
    }

    previewRoot.innerHTML = "";
    const activeCount = clampCount(count);
    if (!activeCount) {
        const empty = document.createElement("div");
        empty.textContent = "Nenhuma referencia ativa.";
        empty.style.opacity = "0.7";
        empty.style.fontSize = "12px";
        previewRoot.appendChild(empty);
        return;
    }

    for (let index = 0; index < activeCount; index += 1) {
        const widget = referenceWidgets[index];
        const imageName = widget?.value;
        if (!imageName) {
            continue;
        }

        const card = document.createElement("div");
        card.style.display = "flex";
        card.style.flexDirection = "column";
        card.style.gap = "4px";

        const label = document.createElement("div");
        label.textContent = `Ref ${index + 1}: ${String(imageName)}`;
        label.style.fontSize = "11px";
        label.style.whiteSpace = "nowrap";
        label.style.overflow = "hidden";
        label.style.textOverflow = "ellipsis";

        const image = document.createElement("img");
        image.src = resolveInputImageUrl(imageName);
        image.loading = "lazy";
        image.alt = `Reference ${index + 1}`;
        image.style.display = "block";
        image.style.width = "100%";
        image.style.height = "100%";
        image.style.objectFit = "contain";
        image.style.border = "1px solid rgba(255,255,255,0.15)";
        image.style.borderRadius = "4px";
        image.style.background = "rgba(0, 0, 0, 0.18)";
        image.style.minHeight = "120px";
        image.addEventListener("error", () => {
            image.style.display = "none";
        });

        card.appendChild(label);
        card.appendChild(image);
        previewRoot.appendChild(card);
    }

    if (!previewRoot.childElementCount) {
        const empty = document.createElement("div");
        empty.textContent = "Selecione uma imagem nas referencias ativas.";
        empty.style.opacity = "0.7";
        empty.style.fontSize = "12px";
        previewRoot.appendChild(empty);
    }
}

function createPreviewWidget(node, getReferenceCount) {
    const container = document.createElement("div");
    container.style.display = "grid";
    container.style.gridTemplateColumns = "1fr";
    container.style.gap = "8px";
    container.style.width = "100%";
    container.style.height = "26px";
    container.style.maxHeight = "26px";
    container.style.overflowY = "auto";
    container.style.padding = "2px";

    const widget = node.addDOMWidget(
        "references_preview",
        "diztraido-reference-preview",
        container,
        { serialize: false, hideOnZoom: false },
    );

    const layoutState = {
        previewHeight: 26,
        expandedPreviewHeight: 180,
        lastNodeHeight: Number(node?.size?.[1]) || null,
        lastReferenceCount: clampCount(getReferenceCount?.() ?? 0),
    };

    const setPreviewHeight = (height) => {
        const previewHeight = Math.max(26, Math.round(height));
        layoutState.previewHeight = previewHeight;
        container.style.height = `${previewHeight - 10}px`;
        container.style.maxHeight = `${previewHeight - 10}px`;
        return previewHeight;
    };

    const syncLayout = ({ fromResize = false } = {}) => {
        const currentCount = clampCount(getReferenceCount?.() ?? 0);
        const nodeHeight = Number(node?.size?.[1]) || layoutState.lastNodeHeight;

        if (fromResize && nodeHeight && layoutState.lastNodeHeight && currentCount > 0) {
            const deltaHeight = nodeHeight - layoutState.lastNodeHeight;
            if (deltaHeight) {
                layoutState.expandedPreviewHeight = Math.max(160, layoutState.expandedPreviewHeight + deltaHeight);
            }
        }

        if (currentCount <= 0) {
            setPreviewHeight(26);
        } else if (layoutState.lastReferenceCount <= 0) {
            setPreviewHeight(layoutState.expandedPreviewHeight);
        } else {
            setPreviewHeight(layoutState.previewHeight || layoutState.expandedPreviewHeight);
        }

        if (currentCount > 0) {
            layoutState.expandedPreviewHeight = Math.max(160, layoutState.previewHeight);
        }

        layoutState.lastReferenceCount = currentCount;
        layoutState.lastNodeHeight = nodeHeight;
        return layoutState.previewHeight;
    };

    widget.computeSize = (width) => {
        const previewHeight = syncLayout();
        return [Math.max(0, width), previewHeight];
    };

    syncLayout();
    return { container, syncLayout };
}

function createControls(node, countWidget, referenceWidgets, onChanged) {
    const controls = document.createElement("div");
    controls.style.display = "flex";
    controls.style.gap = "6px";
    controls.style.width = "100%";
    controls.style.height = "100%";
    controls.style.boxSizing = "border-box";
    controls.style.paddingBottom = "8px";

    const addButton = document.createElement("button");
    addButton.type = "button";
    addButton.textContent = "Add Reference";
    addButton.style.flex = "1";

    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.textContent = "Remove";
    removeButton.style.flex = "1";

    const stopPointer = (event) => event.stopPropagation();
    addButton.addEventListener("pointerdown", stopPointer);
    removeButton.addEventListener("pointerdown", stopPointer);

    addButton.addEventListener("click", (event) => {
        event.preventDefault();
        countWidget.value = clampCount((countWidget.value ?? 0) + 1);
        updateVisibleReferences(node, countWidget, referenceWidgets);
        onChanged?.();
    });

    removeButton.addEventListener("click", (event) => {
        event.preventDefault();
        countWidget.value = clampCount((countWidget.value ?? 0) - 1);
        updateVisibleReferences(node, countWidget, referenceWidgets);
        onChanged?.();
    });

    controls.appendChild(addButton);
    controls.appendChild(removeButton);

    const domWidget = node.addDOMWidget(
        "references_controls",
        "diztraido-reference-controls",
        controls,
        { serialize: false, hideOnZoom: false },
    );
    domWidget.computeSize = () => [0, 40];
}

function fitNodeToContent(node, minWidth = 540) {
    if (!node || typeof node.computeSize !== "function" || typeof node.setSize !== "function") {
        return;
    }
    const computed = node.computeSize();
    const width = Math.max(minWidth, Number(computed?.[0]) || minWidth);
    const height = Math.max(0, Number(computed?.[1]) || 0);
    node.setSize([width, height]);
}

app.registerExtension({
    name: "diztraido.ReferenceChain",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_CLASS) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        const originalOnConfigure = nodeType.prototype.onConfigure;

        nodeType.prototype.onConfigure = function () {
            const result = originalOnConfigure?.apply(this, arguments);
            const sync = this.__diztraidoSyncReferences;
            if (typeof sync === "function") {
                // Aguarda a restauracao dos widgets do workflow antes de sincronizar a UI.
                defer(sync, 2);
            }
            return result;
        };

        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            const node = this;

            const countWidget = this.widgets?.find((widget) => widget.name === "reference_count");
            const referenceWidgets = getReferenceWidgets(this);
            if (!countWidget || !referenceWidgets.length) {
                return result;
            }

            const previewWidget = createPreviewWidget(
                node,
                () => clampCount(countWidget?.value ?? 0),
            );
            const previewRoot = previewWidget.container;

            const refreshPreview = () => {
                renderReferencesPreview(previewRoot, countWidget.value, referenceWidgets);
                previewWidget.syncLayout();
                disableNativePreview(node);
                node.setDirtyCanvas(true, true);
            };

            const syncState = () => {
                updateVisibleReferences(node, countWidget, referenceWidgets);
                refreshPreview();
            };
            node.__diztraidoSyncReferences = syncState;

            const originalCallback = countWidget.callback;
            countWidget.callback = function (value) {
                const callbackResult = originalCallback?.apply(this, arguments);
                countWidget.value = clampCount(value ?? countWidget.value);
                updateVisibleReferences(node, countWidget, referenceWidgets);
                refreshPreview();
                return callbackResult;
            };

            referenceWidgets.forEach((widget) => {
                if (!widget) {
                    return;
                }
                const originalImageCallback = widget.callback;
                widget.callback = function (value) {
                    const callbackResult = originalImageCallback?.apply(this, arguments);
                    if (value !== undefined) {
                        widget.value = value;
                    }
                    refreshPreview();
                    return callbackResult;
                };
            });

            createControls(node, countWidget, referenceWidgets, syncState);
            syncState();
            defer(syncState, 2);

            // Evita faixa vazia inicial: o no nasce com altura real dos widgets.
            defer(() => {
                fitNodeToContent(node, 540);
                refreshPreview();
            }, 2);

            const originalOnResize = node.onResize;
            node.onResize = function () {
                const resizeResult = originalOnResize?.apply(this, arguments);
                previewWidget.syncLayout({ fromResize: true });
                disableNativePreview(node);
                return resizeResult;
            };

            const originalOnDrawBackground = node.onDrawBackground;
            node.onDrawBackground = function (ctx) {
                disableNativePreview(node);
                return originalOnDrawBackground?.call(this, ctx);
            };
            return result;
        };
    },
});
