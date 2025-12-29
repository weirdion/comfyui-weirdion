/**
 * ComfyUI web extension for weirdion_PromptWithEmbedding node
 *
 * This extension handles dropdown insertion for embedding selectors.
 */

import { app } from "../../scripts/app.js";

function insertAtCursor(widget, text) {
    const inputEl = widget.inputEl;
    const currentText = inputEl ? inputEl.value : (widget.value || "");

    if (!inputEl || inputEl.selectionStart === undefined || inputEl.selectionEnd === undefined) {
        const newText = `${currentText}${text}`;
        widget.value = newText;
        if (inputEl) {
            inputEl.value = newText;
        }
        return;
    }

    const start = inputEl.selectionStart;
    const end = inputEl.selectionEnd;
    const newText = `${currentText.slice(0, start)}${text}${currentText.slice(end)}`;
    widget.value = newText;
    inputEl.value = newText;

    const cursor = start + text.length;
    inputEl.setSelectionRange(cursor, cursor);
    inputEl.focus();
}

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
                        const embeddingTag = `embedding:${value}`;
                        insertAtCursor(promptWidget, embeddingTag);
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
