/**
 * ComfyUI web extension for weirdion_PromptWithEmbedding node
 *
 * This extension handles dropdown insertion for embedding selectors.
 */

import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "weirdion.PromptWithEmbedding",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "weirdion_PromptWithEmbedding") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);

                const promptWidget = this.widgets.find(w => w.name === "prompt");
                const embeddingWidget = this.widgets.find(w => w.name === "embedding");

                if (!promptWidget || !embeddingWidget) {
                    console.error("[weirdion] Could not find required widgets");
                    return result;
                }

                const originalEmbeddingCallback = embeddingWidget.callback;
                embeddingWidget.callback = function(value) {
                    if (value && value !== "Insert Embedding") {
                        const currentText = promptWidget.value || "";
                        const embeddingTag = `embedding:${value}`;

                        const newText = `${currentText}${embeddingTag}`;

                        promptWidget.value = newText;
                        embeddingWidget.value = "Insert Embedding";
                    }

                    if (originalEmbeddingCallback) {
                        originalEmbeddingCallback.apply(this, arguments);
                    }
                };

                return result;
            };
        }
    }
});
