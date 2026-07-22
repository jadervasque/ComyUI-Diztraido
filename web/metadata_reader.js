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

async function refreshMetadata(node, imageName, metadataWidget) {
    if (!imageName) {
        setText(metadataWidget, EMPTY_MESSAGE);
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
                metadataWidget.inputEl.style.opacity = 0.85;
            }
            setText(metadataWidget, EMPTY_MESSAGE);

            const node = this;
            const originalCallback = imageWidget.callback;
            imageWidget.callback = function (value) {
                const callbackResult = originalCallback?.apply(this, arguments);
                refreshMetadata(
                    node,
                    value ?? imageWidget.value,
                    metadataWidget,
                );
                return callbackResult;
            };

            this.setSize([560, 500]);
            requestAnimationFrame(() => {
                refreshMetadata(this, imageWidget.value, metadataWidget);
            });
            return result;
        };
    },
});
