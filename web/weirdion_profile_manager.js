/**
 * Profile Manager UI + Load Profile Input Parameters helpers.
 */

import { app } from "../../scripts/app.js";

const EXTENSION_NAME = "weirdion.ProfileManager";
const DEFAULT_PROFILE_NAME = "Default";
const UNSAVED_SUFFIX = " (unsaved)";
const API_URL = "/weirdion/profiles";
const CSS_URL = "/extensions/comfyui-weirdion/weirdion_profile_manager.css";
const PARAM_WIDGET_NAMES = ["steps", "cfg", "sampler", "scheduler", "denoise", "clip_skip"];

function stripUnsaved(name) {
    if (!name) {
        return "";
    }
    if (name.endsWith(UNSAVED_SUFFIX)) {
        return name.slice(0, -UNSAVED_SUFFIX.length);
    }
    return name;
}

function toUnsaved(name) {
    if (!name) {
        return "";
    }
    if (name.endsWith(UNSAVED_SUFFIX)) {
        return name;
    }
    return `${name}${UNSAVED_SUFFIX}`;
}

function addCssLink(href) {
    if (document.querySelector(`link[href="${href}"]`)) {
        return;
    }
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
}

function showToast(message, type = "info", timeoutMs = 3000) {
    const toast = document.createElement("div");
    toast.className = `weirdion-toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), timeoutMs);
}

async function fetchProfiles() {
    const res = await fetch(API_URL, { method: "GET" });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data?.error || "Failed to load profiles");
    }
    return data;
}

async function saveProfiles(payload) {
    const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data?.error || "Failed to save profiles");
    }
    return data;
}

function normalizeProfile(profile) {
    return {
        steps: Number(profile.steps ?? 30),
        cfg: Number(profile.cfg ?? 5),
        sampler: profile.sampler ?? "euler_ancestral",
        scheduler: profile.scheduler ?? "karras",
        denoise: Number(profile.denoise ?? 1.0),
        clip_skip: Number(profile.clip_skip ?? -2),
        note: profile.note ?? "",
        checkpoints: Array.isArray(profile.checkpoints) ? profile.checkpoints : [],
    };
}

function resolveProfileData(data, checkpointName, profileName) {
    if (!data) {
        return null;
    }

    const baseName = stripUnsaved(profileName || DEFAULT_PROFILE_NAME) || DEFAULT_PROFILE_NAME;
    if (baseName === DEFAULT_PROFILE_NAME) {
        const mapped = data.checkpoint_defaults?.[checkpointName];
        if (mapped && data.profiles?.[mapped]) {
            return normalizeProfile(data.profiles[mapped]);
        }
        return normalizeProfile(data.default_profile || {});
    }

    const profile = data.profiles?.[baseName];
    return profile ? normalizeProfile(profile) : null;
}

function resolveProfileNote(data, checkpointName, profileName) {
    const profileData = resolveProfileData(data, checkpointName, profileName);
    return profileData?.note || "";
}

function setProfileValues(node, profileData) {
    if (!profileData) {
        return;
    }
    const widgets = node.widgets || [];
    const wasApplying = node._weirdionApplying;
    node._weirdionApplying = true;
    PARAM_WIDGET_NAMES.forEach((name) => {
        const widget = widgets.find((w) => w.name === name);
        if (!widget) {
            return;
        }
        if (name === "steps" || name === "clip_skip") {
            widget.value = Number.parseInt(profileData[name], 10);
        } else if (name === "cfg" || name === "denoise") {
            widget.value = Number.parseFloat(profileData[name]);
        } else {
            widget.value = profileData[name];
        }
    });
    node._weirdionApplying = wasApplying;
}

class ProfileManagerUI {
    constructor() {
        this.data = null;
        this.selectedProfile = DEFAULT_PROFILE_NAME;
        this.overlay = document.createElement("div");
        this.modal = document.createElement("div");
        this.overlay.className = "weirdion-profile-overlay";
        this.modal.className = "weirdion-profile-modal";
        this.modal.innerHTML = this._template();
        document.body.appendChild(this.overlay);
        document.body.appendChild(this.modal);
        this._bindEvents();
    }

    _template() {
        return `
            <div class="weirdion-profile-shell">
                <div class="weirdion-profile-nav">
                    <h3>Weirdion</h3>
                    <div class="nav-item active">Profile Manager</div>
                </div>
                <div class="weirdion-profile-content">
                    <div class="weirdion-profile-list">
                        <div class="weirdion-profile-actions">
                            <button class="weirdion-button primary" data-action="new">New</button>
                            <button class="weirdion-button" data-action="save">Save</button>
                            <button class="weirdion-button" data-action="save-as">Save As</button>
                            <button class="weirdion-button danger" data-action="delete">Delete</button>
                        </div>
                        <div data-role="profile-list"></div>
                    </div>
                    <div>
                        <div class="weirdion-profile-form">
                            <div class="field">
                                <label>Name</label>
                                <input type="text" data-field="name" />
                            </div>
                            <div class="field">
                                <label>Steps</label>
                                <input type="number" min="1" data-field="steps" />
                            </div>
                            <div class="field">
                                <label>CFG</label>
                                <input type="number" step="0.1" data-field="cfg" />
                            </div>
                            <div class="field">
                                <label>Sampler</label>
                                <input type="text" data-field="sampler" />
                            </div>
                            <div class="field">
                                <label>Scheduler</label>
                                <input type="text" data-field="scheduler" />
                            </div>
                            <div class="field">
                                <label>Denoise</label>
                                <input type="number" step="0.01" data-field="denoise" />
                            </div>
                            <div class="field">
                                <label>Clip Skip</label>
                                <input type="number" step="1" data-field="clip_skip" />
                            </div>
                            <div class="field" style="grid-column: span 3;">
                                <label>Note</label>
                                <textarea data-field="note"></textarea>
                            </div>
                            <div class="weirdion-checkpoints">
                                <label>Checkpoint Associations</label>
                                <div class="weirdion-checkpoint-chips" data-role="checkpoint-chips"></div>
                            </div>
                            <div class="weirdion-profile-note" data-role="profile-hint"></div>
                        </div>
                    </div>
                </div>
                <div class="weirdion-profile-footer">
                    <button class="weirdion-button" data-action="close">Close</button>
                </div>
            </div>
        `;
    }

    _bindEvents() {
        this.overlay.addEventListener("click", () => this.close());
        this.modal.addEventListener("click", (event) => {
            const target = event.target;
            if (!(target instanceof HTMLElement)) {
                return;
            }
            const action = target.getAttribute("data-action");
            if (!action) {
                return;
            }
            event.preventDefault();
            this._handleAction(action);
        });
    }

    async open() {
        try {
            this.data = await fetchProfiles();
            this.data.profiles = this.data.profiles || {};
            this.data.checkpoint_defaults = this.data.checkpoint_defaults || {};
            this.data.checkpoints = this.data.checkpoints || [];
            window.weirdionProfileData = this.data;
            this._render();
            this.overlay.classList.add("is-open");
            this.modal.classList.add("is-open");
        } catch (error) {
            showToast(error.message || "Failed to open Profile Manager", "error");
        }
    }

    close() {
        this.overlay.classList.remove("is-open");
        this.modal.classList.remove("is-open");
    }

    _handleAction(action) {
        if (action === "close") {
            this.close();
            return;
        }

        if (!this.data) {
            return;
        }

        if (action === "new") {
            this._selectProfile("");
            return;
        }

        if (action === "save") {
            this._saveProfile(false);
            return;
        }

        if (action === "save-as") {
            this._saveProfile(true);
            return;
        }

        if (action === "delete") {
            this._deleteProfile();
        }
    }

    _render() {
        this._renderProfileList();
        this._renderForm();
        this._renderCheckpointChips();
    }

    _renderProfileList() {
        const listEl = this.modal.querySelector('[data-role="profile-list"]');
        listEl.innerHTML = "";

        const profiles = this.data.profiles || {};
        const names = [DEFAULT_PROFILE_NAME, ...Object.keys(profiles).sort()];

        names.forEach((name) => {
            const pill = document.createElement("div");
            pill.className = "weirdion-profile-pill";
            if (name === this.selectedProfile) {
                pill.classList.add("active");
            }
            pill.innerHTML = `<span>${name}</span><span class="pill-tag">${name === DEFAULT_PROFILE_NAME ? "default" : "user"}</span>`;
            pill.addEventListener("click", () => this._selectProfile(name));
            listEl.appendChild(pill);
        });
    }

    _renderForm() {
        const profile = this._getSelectedProfileData();
        const isDefault = this.selectedProfile === DEFAULT_PROFILE_NAME;

        const fields = this.modal.querySelectorAll("[data-field]");
        fields.forEach((field) => {
            const key = field.getAttribute("data-field");
            if (key === "name") {
                field.value = this.selectedProfile || "";
                field.disabled = isDefault;
                return;
            }
            if (!profile) {
                field.value = "";
                field.disabled = isDefault;
                return;
            }
            field.value = profile[key] ?? "";
            field.disabled = isDefault;
        });

        const hintEl = this.modal.querySelector('[data-role="profile-hint"]');
        if (isDefault) {
            hintEl.textContent = "Default profile is read-only.";
        } else {
            hintEl.textContent = "";
        }
    }

    _renderCheckpointChips() {
        const chipsEl = this.modal.querySelector('[data-role="checkpoint-chips"]');
        chipsEl.innerHTML = "";

        const profile = this._getSelectedProfileData();
        const isDefault = this.selectedProfile === DEFAULT_PROFILE_NAME;
        const checkpoints = this.data.checkpoints || [];

        const associated = new Set(profile?.checkpoints || []);
        const allNames = [...new Set([...checkpoints, ...associated])].sort();
        const defaults = this.data.checkpoint_defaults || {};

        allNames.forEach((ckpt) => {
            const chip = document.createElement("span");
            chip.className = "weirdion-chip";
            if (associated.has(ckpt)) {
                chip.classList.add("selected");
            }
            if (!checkpoints.includes(ckpt)) {
                chip.classList.add("missing");
            }

            const star = document.createElement("span");
            star.className = "star";
            star.textContent = defaults[ckpt] === this.selectedProfile ? "★" : "☆";

            const label = document.createElement("span");
            label.textContent = ckpt;

            chip.appendChild(star);
            chip.appendChild(label);

            chip.addEventListener("click", () => {
                if (isDefault) {
                    return;
                }
                this._toggleCheckpointAssociation(ckpt);
            });

            star.addEventListener("click", (event) => {
                event.stopPropagation();
                if (isDefault) {
                    return;
                }
                this._toggleCheckpointDefault(ckpt);
            });

            chipsEl.appendChild(chip);
        });
    }

    _toggleCheckpointAssociation(ckpt) {
        if (!this.selectedProfile) {
            showToast("Save the profile before assigning checkpoints.", "error");
            return;
        }
        const profile = this.data.profiles?.[this.selectedProfile];
        if (!profile) {
            return;
        }
        const checkpoints = new Set(profile.checkpoints || []);
        if (checkpoints.has(ckpt)) {
            checkpoints.delete(ckpt);
            if (this.data.checkpoint_defaults[ckpt] === this.selectedProfile) {
                delete this.data.checkpoint_defaults[ckpt];
            }
        } else {
            checkpoints.add(ckpt);
        }
        profile.checkpoints = Array.from(checkpoints);
        this._renderCheckpointChips();
    }

    _toggleCheckpointDefault(ckpt) {
        if (!this.selectedProfile) {
            showToast("Save the profile before setting defaults.", "error");
            return;
        }
        if (this.data.checkpoint_defaults[ckpt] === this.selectedProfile) {
            delete this.data.checkpoint_defaults[ckpt];
        } else {
            this.data.checkpoint_defaults[ckpt] = this.selectedProfile;
        }
        this._renderCheckpointChips();
    }

    _selectProfile(name) {
        if (!this.data) {
            return;
        }
        this.selectedProfile = name || "";
        if (!name) {
            this.selectedProfile = "";
        } else if (!this.data.profiles[name] && name !== DEFAULT_PROFILE_NAME) {
            this.selectedProfile = DEFAULT_PROFILE_NAME;
        }
        this._renderProfileList();
        this._renderForm();
        this._renderCheckpointChips();
    }

    _getSelectedProfileData() {
        if (!this.data) {
            return null;
        }
        if (this.selectedProfile === DEFAULT_PROFILE_NAME) {
            return normalizeProfile(this.data.default_profile || {});
        }
        if (!this.selectedProfile) {
            return normalizeProfile(this.data.default_profile || {});
        }
        const profile = this.data.profiles[this.selectedProfile];
        return profile ? normalizeProfile(profile) : null;
    }

    async _saveProfile(saveAs) {
        const nameInput = this.modal.querySelector('[data-field="name"]');
        let name = nameInput.value.trim();

        if (this.selectedProfile === DEFAULT_PROFILE_NAME && !saveAs) {
            showToast("Default profile is read-only.", "error");
            return;
        }

        if (saveAs || !name) {
            const promptName = window.prompt("Profile name:", name || "");
            if (!promptName) {
                return;
            }
            name = promptName.trim();
        }

        if (!name) {
            showToast("Profile name is required.", "error");
            return;
        }

        if (name === DEFAULT_PROFILE_NAME) {
            showToast("Profile name cannot be 'Default'.", "error");
            return;
        }

        const payload = this._readForm();
        const existing = this.data.profiles[name];
        payload.checkpoints = existing?.checkpoints || payload.checkpoints || [];

        this.data.profiles[name] = payload;
        this.selectedProfile = name;

        try {
            await saveProfiles({
                profiles: this.data.profiles,
                checkpoint_defaults: this.data.checkpoint_defaults,
            });
            window.weirdionProfileData = this.data;
            window.dispatchEvent(new CustomEvent("weirdion:profiles-updated"));
            showToast("Profile saved.");
            this._render();
        } catch (error) {
            showToast(error.message || "Failed to save profile", "error");
        }
    }

    async _deleteProfile() {
        if (this.selectedProfile === DEFAULT_PROFILE_NAME) {
            showToast("Default profile cannot be deleted.", "error");
            return;
        }
        if (!this.selectedProfile) {
            return;
        }

        const ok = window.confirm(`Delete profile '${this.selectedProfile}'?`);
        if (!ok) {
            return;
        }

        delete this.data.profiles[this.selectedProfile];
        Object.keys(this.data.checkpoint_defaults).forEach((ckpt) => {
            if (this.data.checkpoint_defaults[ckpt] === this.selectedProfile) {
                delete this.data.checkpoint_defaults[ckpt];
            }
        });
        this.selectedProfile = DEFAULT_PROFILE_NAME;

        try {
            await saveProfiles({
                profiles: this.data.profiles,
                checkpoint_defaults: this.data.checkpoint_defaults,
            });
            window.weirdionProfileData = this.data;
            window.dispatchEvent(new CustomEvent("weirdion:profiles-updated"));
            showToast("Profile deleted.");
            this._render();
        } catch (error) {
            showToast(error.message || "Failed to delete profile", "error");
        }
    }

    _readForm() {
        const fields = this.modal.querySelectorAll("[data-field]");
        const payload = {};
        fields.forEach((field) => {
            const key = field.getAttribute("data-field");
            if (key === "name") {
                return;
            }
            payload[key] = field.value;
        });

        return normalizeProfile(payload);
    }
}

function addMenuButton() {
    const buttonGroup = document.querySelector(".comfyui-button-group");
    if (!buttonGroup) {
        setTimeout(addMenuButton, 500);
        return;
    }

    if (document.getElementById("weirdion-profile-button")) {
        return;
    }

    const button = document.createElement("button");
    button.textContent = "Profile Manager";
    button.id = "weirdion-profile-button";
    button.title = "Open Profile Manager";

    button.addEventListener("click", async () => {
        if (!window.weirdionProfileManager) {
            window.weirdionProfileManager = new ProfileManagerUI();
        }
        await window.weirdionProfileManager.open();
    });

    buttonGroup.appendChild(button);
}

function applyProfileFilters(node) {
    const profileWidget = node.widgets?.find((w) => w.name === "profile");
    if (!profileWidget) {
        return;
    }

    const checkpointWidget = node.widgets?.find((w) => w.name === "checkpoint_name");
    const checkpointName =
        checkpointWidget?.value === "Select Checkpoint" ? "" : checkpointWidget?.value || "";
    const data = window.weirdionProfileData;
    const baseProfile = node._weirdionProfileDirty
        ? node._weirdionProfileBase || DEFAULT_PROFILE_NAME
        : stripUnsaved(profileWidget.value || DEFAULT_PROFILE_NAME) || DEFAULT_PROFILE_NAME;
    const wasApplying = node._weirdionApplying;
    node._weirdionApplying = true;

    try {
        if (!data) {
            profileWidget.options.values = [DEFAULT_PROFILE_NAME];
            profileWidget.value = DEFAULT_PROFILE_NAME;
            return;
        }

        const profiles = data.profiles || {};
        const associated = Object.keys(profiles).filter((name) =>
            (profiles[name].checkpoints || []).includes(checkpointName)
        );
        const unassigned = Object.keys(profiles).filter(
            (name) => (profiles[name].checkpoints || []).length === 0
        );

        const values = [DEFAULT_PROFILE_NAME, ...associated, ...unassigned];
        let unique = Array.from(new Set(values));

        if (node._weirdionProfileDirty) {
            const unsaved = toUnsaved(baseProfile);
            if (!unique.includes(unsaved)) {
                unique = [unsaved, ...unique];
            }
            profileWidget.value = unsaved;
        } else {
            if (!unique.includes(baseProfile)) {
                profileWidget.value = DEFAULT_PROFILE_NAME;
                node._weirdionProfileBase = DEFAULT_PROFILE_NAME;
            } else {
                profileWidget.value = baseProfile;
                node._weirdionProfileBase = baseProfile;
            }
        }
        profileWidget.options.values = unique;

        const noteWidget = node.widgets?.find((w) => w.name === "profile_note");
        if (noteWidget) {
            noteWidget.value = resolveProfileNote(data, checkpointName, baseProfile);
        }

        if (!node._weirdionProfileDirty) {
            const profileData = resolveProfileData(data, checkpointName, baseProfile);
            setProfileValues(node, profileData);
        }
    } finally {
        node._weirdionApplying = wasApplying;
    }
}

app.registerExtension({
    name: EXTENSION_NAME,
    async setup() {
        addCssLink(CSS_URL);
        addMenuButton();

        try {
            window.weirdionProfileData = await fetchProfiles();
        } catch (error) {
            console.warn("[weirdion] Failed to preload profiles", error);
        }

        window.addEventListener("weirdion:profiles-updated", async () => {
            try {
                window.weirdionProfileData = await fetchProfiles();
            } catch (error) {
                console.warn("[weirdion] Failed to refresh profiles", error);
            }
        });
    },

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "weirdion_LoadProfileInputParameters") {
            return;
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated?.apply(this, arguments);

            const noteWidget = this.addWidget("text", "profile_note", "", () => {});
            if (noteWidget?.inputEl) {
                noteWidget.inputEl.disabled = true;
            }
            noteWidget.serializeValue = () => "";

            const checkpointWidget = this.widgets?.find((w) => w.name === "checkpoint_name");
            if (checkpointWidget) {
                const originalCallback = checkpointWidget.callback;
                const node = this;
                checkpointWidget.callback = function () {
                    if (originalCallback) {
                        originalCallback.apply(this, arguments);
                    }
                    if (node._weirdionApplying) {
                        return;
                    }
                    node._weirdionProfileDirty = false;
                    node._weirdionProfileBase = stripUnsaved(
                        node.widgets?.find((w) => w.name === "profile")?.value || DEFAULT_PROFILE_NAME
                    );
                    applyProfileFilters(node);
                };
            }

            const profileWidget = this.widgets?.find((w) => w.name === "profile");
            if (profileWidget) {
                const originalProfileCallback = profileWidget.callback;
                const node = this;
                profileWidget.callback = function () {
                    if (originalProfileCallback) {
                        originalProfileCallback.apply(this, arguments);
                    }
                    if (node._weirdionApplying) {
                        return;
                    }
                    node._weirdionProfileDirty = false;
                    node._weirdionProfileBase =
                        stripUnsaved(profileWidget.value || DEFAULT_PROFILE_NAME) || DEFAULT_PROFILE_NAME;
                    applyProfileFilters(node);
                };
            }

            PARAM_WIDGET_NAMES.forEach((name) => {
                const widget = this.widgets?.find((w) => w.name === name);
                if (!widget) {
                    return;
                }
                const originalCallback = widget.callback;
                const node = this;
                widget.callback = function () {
                    if (originalCallback) {
                        originalCallback.apply(this, arguments);
                    }
                    if (node._weirdionApplying) {
                        return;
                    }
                    node._weirdionProfileDirty = true;
                    node._weirdionProfileBase = stripUnsaved(
                        node.widgets?.find((w) => w.name === "profile")?.value || DEFAULT_PROFILE_NAME
                    );
                    applyProfileFilters(node);
                };
            });

            this._weirdionProfileDirty = false;
            this._weirdionProfileBase = DEFAULT_PROFILE_NAME;
            applyProfileFilters(this);
            return result;
        };
    },
});
