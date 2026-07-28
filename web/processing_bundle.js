import { app } from "../../scripts/app.js";

const NODE_CLASS = "DiztraidoProcessingBundle";

function hideSerializedWidget(widget) {
    if (!widget || widget.__diztraidoHiddenSerialized) {
        return;
    }
    widget.__diztraidoHiddenSerialized = true;
    widget.hidden = true;
    widget.type = "diztraido-hidden-widget";
    widget.computeSize = () => [0, -4];
    widget.options = { ...(widget.options ?? {}), serialize: true };
}

function configureDecodeTracking(node) {
    if (node.__diztraidoDecodeTrackingConfigured) {
        return;
    }

    const decodeWidget = node.widgets?.find((widget) => widget.name === "decode_image");
    if (!decodeWidget) {
        return;
    }
    hideSerializedWidget(decodeWidget);

    const sync = () => {
        const imageOutput = node.outputs?.[0];
        const connected = Array.isArray(imageOutput?.links) && imageOutput.links.length > 0;
        if (decodeWidget.value !== connected) {
            decodeWidget.value = connected;
            decodeWidget.callback?.(connected);
        }
        node.setDirtyCanvas?.(true, true);
    };

    const originalConnectionsChange = node.onConnectionsChange;
    node.onConnectionsChange = function () {
        const result = originalConnectionsChange?.apply(this, arguments);
        requestAnimationFrame(sync);
        return result;
    };

    node.__diztraidoSyncDecodeImage = sync;
    node.__diztraidoDecodeTrackingConfigured = true;
    requestAnimationFrame(sync);
}

app.registerExtension({
    name: "diztraido.ProcessingBundle",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== NODE_CLASS) {
            return;
        }

        const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = originalOnNodeCreated?.apply(this, arguments);
            configureDecodeTracking(this);
            return result;
        };

        const originalOnConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const result = originalOnConfigure?.apply(this, arguments);
            requestAnimationFrame(() => {
                configureDecodeTracking(this);
                this.__diztraidoSyncDecodeImage?.();
            });
            return result;
        };
    },
});
