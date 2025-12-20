/**
 * ComfyUI web extension for weirdion_PromptWithLora node
 *
 * This extension handles the dropdown insertions for LoRA and embedding selectors.
 * When a user selects a LoRA or embedding from the dropdown, it automatically
 * inserts the appropriate tag into the prompt text field and resets the dropdown.
 */

import { app } from "../../scripts/app.js";

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
                        // Get current cursor position or append to end
                        const currentText = promptWidget.value || "";
                        const loraTag = `<lora:${value}:1.0>`;

                        // Insert at end with proper separator
                        const newText = `${currentText}${loraTag}`;

                        promptWidget.value = newText;

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
                        // Get current cursor position or append to end
                        const currentText = promptWidget.value || "";
                        const embeddingTag = `embedding:${value}`;

                        // Insert at end with proper separator
                        const newText = `${currentText}${embeddingTag}`;

                        promptWidget.value = newText;

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
