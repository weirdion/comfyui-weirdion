/**
 * ComfyUI web extension for weirdion_PromptWithLora node
 *
 * This extension handles the dropdown insertions for LoRA and embedding selectors.
 * When a user selects a LoRA or embedding from the dropdown, it automatically
 * inserts the appropriate tag into the prompt text field and resets the dropdown.
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
    name: "weirdion.PromptWithLora",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "weirdion_PromptWithLora") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);

                // Find the widgets
                const promptWidget = this.widgets.find(w => w.name === "prompt");
                const loraWidget = this.widgets.find(w => w.name === "lora");
                const embeddingWidget = this.widgets.find(w => w.name === "embedding");

                if (!promptWidget || !loraWidget || !embeddingWidget) {
                    console.error("[weirdion] Could not find required widgets");
                    return result;
                }

                // Store original callback for LoRA dropdown
                const originalLoraCallback = loraWidget.callback;
                loraWidget.callback = function(value) {
                    if (value && value !== "Insert LoRA") {
                        const loraTag = `<lora:${value}:1.0>`;
                        insertAtCursor(promptWidget, loraTag);

                        // Reset dropdown to CHOOSE
                        loraWidget.value = "Insert LoRA";
                    }

                    // Call original callback if it exists
                    if (originalLoraCallback) {
                        originalLoraCallback.apply(this, arguments);
                    }
                };

                // Store original callback for embedding dropdown
                const originalEmbeddingCallback = embeddingWidget.callback;
                embeddingWidget.callback = function(value) {
                    if (value && value !== "Insert Embedding") {
                        const embeddingTag = `embedding:${value}`;
                        insertAtCursor(promptWidget, embeddingTag);

                        // Reset dropdown to CHOOSE
                        embeddingWidget.value = "Insert Embedding";
                    }

                    // Call original callback if it exists
                    if (originalEmbeddingCallback) {
                        originalEmbeddingCallback.apply(this, arguments);
                    }
                };

                return result;
            };
        }
    }
});
