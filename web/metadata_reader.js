import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const NODE_CLASS = "DiztraidoMetadataReader";
const METADATA_ENDPOINT = "/diztraido/metadata";
const EMPTY_MESSAGE = "Selecione uma imagem para ler os metadados.";

function setText(widget, text) {
    widget.value = text;
    if (widget.inputEl) {
        widget.inputEl.value = text;
    }
}

function escapeHtml(text) {
    return text.replace(/[&<>"']/g, (character) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
    })[character]);
}

function createHighlightLayer(metadataWidget) {
    const input = metadataWidget.inputEl;
    const container = input?.parentElement;
    if (!input || !container || metadataWidget.diztraidoHighlightLayer) {
        return metadataWidget.diztraidoHighlightLayer;
    }

    const inputStyle = getComputedStyle(input);
    const layer = document.createElement("pre");
    Object.assign(layer.style, {
        position: "absolute",
        inset: "0",
        margin: "0",
        padding: inputStyle.padding,
        border: "0",
        boxSizing: "border-box",
        font: inputStyle.font,
        letterSpacing: inputStyle.letterSpacing,
        lineHeight: inputStyle.lineHeight,
        whiteSpace: "pre-wrap",
        overflowWrap: "break-word",
        overflow: "hidden",
        color: inputStyle.color,
        background: "transparent",
        pointerEvents: "none",
        zIndex: "0",
    });
    container.style.position = "relative";
    container.appendChild(layer);
    input.style.position = "relative";
    input.style.zIndex = "1";
    input.style.border = "1px solid #6b7280";
    input.style.borderRadius = "4px";
    input.style.background = "transparent";
    input.style.color = "transparent";
    input.style.caretColor = inputStyle.color;
    input.style.textShadow = "none";
    input.addEventListener("scroll", () => {
        layer.scrollTop = input.scrollTop;
        layer.scrollLeft = input.scrollLeft;
    });

    metadataWidget.diztraidoHighlightLayer = layer;
    return layer;
}

function renderHighlights(metadataWidget, matches, matchIndex, queryLength) {
    const layer = createHighlightLayer(metadataWidget);
    if (!layer) {
        return;
    }

    const text = String(metadataWidget.value ?? "");
    const fragments = [];
    let cursor = 0;
    for (const [index, matchStart] of matches.entries()) {
        fragments.push(escapeHtml(text.slice(cursor, matchStart)));
        const className = index === matchIndex
            ? "diztraido-current-match"
            : "diztraido-match";
        fragments.push(
            '<mark class="' + className + '">'
            + escapeHtml(text.slice(matchStart, matchStart + queryLength))
            + "</mark>",
        );
        cursor = matchStart + queryLength;
    }
    fragments.push(escapeHtml(text.slice(cursor)));
    layer.innerHTML = fragments.join("");

    for (const match of layer.querySelectorAll(".diztraido-match")) {
        Object.assign(match.style, {
            background: "#facc15",
            color: "#111827",
            borderRadius: "2px",
        });
    }
    for (const match of layer.querySelectorAll(".diztraido-current-match")) {
        Object.assign(match.style, {
            background: "#fb923c",
            color: "#111827",
            borderRadius: "2px",
        });
    }
}

function revealMatch(metadataWidget, matchStart, queryLength) {
    const input = metadataWidget.inputEl;
    const layer = metadataWidget.diztraidoHighlightLayer;
    if (!input) {
        return;
    }

    input.setSelectionRange(matchStart, matchStart + queryLength);
    requestAnimationFrame(() => {
        const currentMatch = layer?.querySelector(".diztraido-current-match");
        if (currentMatch) {
            input.scrollTop = Math.max(
                0,
                currentMatch.offsetTop - input.clientHeight / 2 + currentMatch.offsetHeight / 2,
            );
            layer.scrollTop = input.scrollTop;
        }
    });
}

function createNavigationWidget(node, onNavigate) {
    const controls = document.createElement("div");
    Object.assign(controls.style, {
        display: "flex",
        gap: "6px",
        height: "28px",
        width: "100%",
    });

    for (const [label, direction] of [["Anterior", -1], ["Próximo", 1]]) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = label;
        Object.assign(button.style, {
            flex: "1",
            cursor: "pointer",
        });
        button.addEventListener("pointerdown", (event) => event.stopPropagation());
        button.addEventListener("click", (event) => {
            event.preventDefault();
            onNavigate(direction);
        });
        controls.appendChild(button);
    }

    const widget = node.addDOMWidget(
        "navegacao_busca",
        "diztraido-search-navigation",
        controls,
        { serialize: false, hideOnZoom: false },
    );
    widget.computeSize = () => [0, 32];
    return widget;
}

function searchMetadata(metadataWidget, searchWidget, direction = 0) {
    const query = String(searchWidget.inputEl?.value ?? searchWidget.value ?? "").trim();
    const text = String(metadataWidget.value ?? "");
    if (!query) {
        searchWidget.label = "buscar no JSON";
        searchWidget.diztraidoMatches = [];
        searchWidget.diztraidoMatchIndex = -1;
        renderHighlights(metadataWidget, [], -1, 0);
        return;
    }

    const normalizedText = text.toLocaleLowerCase();
    const normalizedQuery = query.toLocaleLowerCase();
    const matches = [];
    let position = normalizedText.indexOf(normalizedQuery);
    while (position !== -1) {
        matches.push(position);
        position = normalizedText.indexOf(normalizedQuery, position + normalizedQuery.length);
    }

    const isNewSearch = (
        searchWidget.diztraidoQuery !== normalizedQuery
        || searchWidget.diztraidoText !== text
    );
    let matchIndex = isNewSearch ? 0 : searchWidget.diztraidoMatchIndex;
    if (direction && matches.length) {
        matchIndex = (matchIndex + direction + matches.length) % matches.length;
    }

    searchWidget.diztraidoQuery = normalizedQuery;
    searchWidget.diztraidoText = text;
    searchWidget.diztraidoMatches = matches;
    searchWidget.diztraidoMatchIndex = matchIndex;
    renderHighlights(metadataWidget, matches, matchIndex, query.length);

    if (!matches.length) {
        searchWidget.label = "buscar: 0 resultados";
        return;
    }

    searchWidget.label = "buscar: " + (matchIndex + 1) + "/" + matches.length;
    const input = metadataWidget.inputEl;
    if (!input) {
        return;
    }

    const matchStart = matches[matchIndex];
    revealMatch(metadataWidget, matchStart, query.length);
}

async function refreshMetadata(node, imageName, metadataWidget, searchWidget) {
    if (!imageName) {
        setText(metadataWidget, EMPTY_MESSAGE);
        searchMetadata(metadataWidget, searchWidget);
        return;
    }

    const requestId = Symbol("metadata request");
    node.diztraidoMetadataRequest = requestId;
    setText(metadataWidget, "Lendo metadados...");

    try {
        const response = await fetch(
            METADATA_ENDPOINT + "?image=" + encodeURIComponent(String(imageName)),
            { cache: "no-store" },
        );
        const payload = await response.json();
        if (node.diztraidoMetadataRequest !== requestId) {
            return;
        }
        if (!response.ok) {
            throw new Error(payload.error || "Não foi possível ler os metadados.");
        }
        setText(metadataWidget, JSON.stringify(payload, null, 2));
    } catch (error) {
        if (node.diztraidoMetadataRequest === requestId) {
            setText(metadataWidget, "Erro: " + error.message);
        }
    }
    searchMetadata(metadataWidget, searchWidget);
    node.graph?.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "diztraido.MetadataReader",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_CLASS) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            const imageWidget = this.widgets?.find((widget) => widget.name === "image");
            if (!imageWidget) {
                return result;
            }

            const searchWidget = ComfyWidgets.STRING(
                this,
                "buscar",
                ["STRING", {}],
                app,
            ).widget;
            searchWidget.serialize = false;
            searchWidget.label = "buscar no JSON";
            if (searchWidget.inputEl) {
                searchWidget.inputEl.placeholder = "Digite para buscar; Enter vai ao próximo";
            }

            let updateSearch = () => {};
            createNavigationWidget(this, (direction) => updateSearch(direction));

            const metadataWidget = ComfyWidgets.STRING(
                this,
                "metadata_json",
                ["STRING", { multiline: true }],
                app,
            ).widget;
            metadataWidget.serialize = false;
            metadataWidget.computeSize = (width) => [width, 320];
            if (metadataWidget.inputEl) {
                metadataWidget.inputEl.readOnly = true;
            }
            setText(metadataWidget, EMPTY_MESSAGE);

            const node = this;
            const originalSearchCallback = searchWidget.callback;
            updateSearch = (direction = 0) => {
                searchMetadata(metadataWidget, searchWidget, direction);
                node.graph?.setDirtyCanvas(true, true);
            };
            searchWidget.callback = function (value) {
                const callbackResult = originalSearchCallback?.apply(this, arguments);
                updateSearch();
                return callbackResult;
            };
            if (searchWidget.inputEl) {
                searchWidget.inputEl.addEventListener("input", () => updateSearch());
                searchWidget.inputEl.addEventListener("keydown", (event) => {
                    if (event.key === "Enter") {
                        event.preventDefault();
                        updateSearch(1);
                    }
                });
            }

            const originalCallback = imageWidget.callback;
            imageWidget.callback = function (value) {
                const callbackResult = originalCallback?.apply(this, arguments);
                refreshMetadata(
                    node,
                    value ?? imageWidget.value,
                    metadataWidget,
                    searchWidget,
                );
                return callbackResult;
            };

            this.setSize([560, 500]);
            requestAnimationFrame(() => {
                refreshMetadata(this, imageWidget.value, metadataWidget, searchWidget);
            });
            return result;
        };
    },
});
