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
const NOTE_DEFAULT_HEIGHT = 160;
const NOTE_MAX_HEIGHT = 160;
const PROFILE_NODES = ["weirdion_LoadProfileInputParameters", "weirdion_LoadCheckpointWithProfiles"];
const PROFILE_NODE_INSTANCES = new Set();

function configureProfileWidget(node, widget) {
    if (widget._weirdionConfigured) {
        return;
    }

    node._weirdionProfileValue =
        stripUnsaved(widget.value || DEFAULT_PROFILE_NAME) || DEFAULT_PROFILE_NAME;

    Object.defineProperty(widget, "value", {
        get() {
            const current = node._weirdionProfileValue || DEFAULT_PROFILE_NAME;
            return node._weirdionProfileDirty ? toUnsaved(current) : current;
        },
        set(value) {
            node._weirdionProfileValue =
                stripUnsaved(value || DEFAULT_PROFILE_NAME) || DEFAULT_PROFILE_NAME;
        },
        configurable: true,
    });

    widget.serializeValue = () => node._weirdionProfileValue || DEFAULT_PROFILE_NAME;
    widget._weirdionConfigured = true;
}

function setNoteHeight(node, height = NOTE_DEFAULT_HEIGHT, syncNodeSize = true) {
    const noteWidget = node?._weirdionNoteWidget;
    const noteEl = noteWidget?.inputEl;
    if (!noteEl || !noteWidget) {
        return;
    }

    noteEl.style.height = `${height}px`;
    noteEl.style.maxHeight = `${height}px`;
    noteWidget.computedHeight = height;
    noteWidget.computeSize = () => [node.size[0], height];

    if (!syncNodeSize) {
        return;
    }

    requestAnimationFrame(() => {
        if (typeof node.setSize === "function") {
            node.setSize([node.size[0], node.computeSize()[1]]);
        } else {
            node.size = [node.size[0], node.computeSize()[1]];
            node.onResize?.(node.size);
        }
        app.graph.setDirtyCanvas(true, false);
    });
}

function updateNoteHeightFromNode(node) {
    const noteWidget = node?._weirdionNoteWidget;
    if (!noteWidget) {
        return;
    }

    const margin = Number.isFinite(noteWidget.margin) ? noteWidget.margin : 4;
    const top = (noteWidget.y ?? 0) + margin;
    const available = Math.min(NOTE_MAX_HEIGHT, Math.max(NOTE_DEFAULT_HEIGHT, node.size[1] - top - margin));
    setNoteHeight(node, available, false);
}

function isProfileDirty(node, profileData) {
    if (!profileData) {
        return false;
    }

    const getWidget = (name) => node.widgets?.find((w) => w.name === name);
    const stepsWidget = getWidget("steps");
    const cfgWidget = getWidget("cfg");
    const samplerWidget = getWidget("sampler");
    const schedulerWidget = getWidget("scheduler");
    const denoiseWidget = getWidget("denoise");
    const clipSkipWidget = getWidget("clip_skip");

    const steps = stepsWidget ? Number.parseInt(stepsWidget.value, 10) : null;
    const cfg = cfgWidget ? Number.parseFloat(cfgWidget.value) : null;
    const sampler = samplerWidget?.value ?? null;
    const scheduler = schedulerWidget?.value ?? null;
    const denoise = denoiseWidget ? Number.parseFloat(denoiseWidget.value) : null;
    const clipSkip = clipSkipWidget ? Number.parseInt(clipSkipWidget.value, 10) : null;

    const epsilon = 1e-6;
    if (steps !== null && steps !== Number.parseInt(profileData.steps, 10)) {
        return true;
    }
    if (cfg !== null && Math.abs(cfg - Number.parseFloat(profileData.cfg)) > epsilon) {
        return true;
    }
    if (sampler !== null && sampler !== profileData.sampler) {
        return true;
    }
    if (scheduler !== null && scheduler !== profileData.scheduler) {
        return true;
    }
    if (denoise !== null && Math.abs(denoise - Number.parseFloat(profileData.denoise)) > epsilon) {
        return true;
    }
    if (clipSkip !== null && clipSkip !== Number.parseInt(profileData.clip_skip, 10)) {
        return true;
    }
    return false;
}

function syncProfileState(node) {
    const data = window.weirdionProfileData;
    if (!data) {
        return;
    }

    const profileWidget = node.widgets?.find((w) => w.name === "profile");
    if (!profileWidget) {
        return;
    }
    configureProfileWidget(node, profileWidget);

    const checkpointWidget = node.widgets?.find((w) => w.name === "checkpoint_name" || w.name === "checkpoint");
    const hasCheckpoint = Boolean(checkpointWidget);
    const checkpointName =
        checkpointWidget?.value === "Select Checkpoint" ? "" : checkpointWidget?.value || "";

    const baseProfile =
        node._weirdionProfileValue || stripUnsaved(profileWidget.value || DEFAULT_PROFILE_NAME) || DEFAULT_PROFILE_NAME;

    const profileData = resolveProfileData(data, checkpointName, baseProfile, hasCheckpoint);
    node._weirdionProfileDirty = isProfileDirty(node, profileData);
    node._weirdionProfileBase = baseProfile;
    applyProfileFilters(node);
}

function addProfileNoteWidget(node) {
    if (typeof node.addDOMWidget === "function") {
        const noteEl = document.createElement("div");
        noteEl.className = "weirdion-profile-note-widget";

        const titleEl = document.createElement("div");
        titleEl.className = "weirdion-profile-note-title";
        titleEl.textContent = "Profile note";

        const bodyEl = document.createElement("div");
        bodyEl.className = "weirdion-profile-note-body";

        noteEl.appendChild(titleEl);
        noteEl.appendChild(bodyEl);

        const widget = node.addDOMWidget("profile_note", "weirdionNote", noteEl, {
            getValue() {
                return bodyEl.textContent || "";
            },
            setValue(value) {
                bodyEl.textContent = value || "";
            },
            serialize: false,
        });
        widget.inputEl = noteEl;
        node._weirdionNoteWidget = widget;
        setNoteHeight(node);
        return widget;
    }

    const fallback = node.addWidget("text", "profile_note", "", () => {});
    if (fallback?.inputEl) {
        fallback.inputEl.disabled = true;
        fallback.inputEl.classList.add("weirdion-profile-note-input");
    }
    fallback.serializeValue = () => "";
    node._weirdionNoteWidget = fallback;
    setNoteHeight(node);
    return fallback;
}

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

function resolveProfileData(data, checkpointName, profileName, allowCheckpointDefaults) {
    if (!data) {
        return null;
    }

    const baseName = stripUnsaved(profileName || DEFAULT_PROFILE_NAME) || DEFAULT_PROFILE_NAME;
    if (baseName === DEFAULT_PROFILE_NAME) {
        if (allowCheckpointDefaults) {
            const mapped = data.checkpoint_defaults?.[checkpointName];
            if (mapped && data.profiles?.[mapped]) {
                return normalizeProfile(data.profiles[mapped]);
            }
        }
        return normalizeProfile(data.default_profile || {});
    }

    const profile = data.profiles?.[baseName];
    return profile ? normalizeProfile(profile) : null;
}

function resolveProfileNote(data, checkpointName, profileName, allowCheckpointDefaults) {
    const profileData = resolveProfileData(data, checkpointName, profileName, allowCheckpointDefaults);
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
                <div class="weirdion-profile-header">
                    <h2>Profile Manager</h2>
                    <button class="weirdion-close-btn" data-action="close" aria-label="Close" title="Close (Esc)">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                <div class="weirdion-profile-content">
                    <aside class="weirdion-profile-sidebar">
                        <div class="weirdion-search-box">
                            <input type="text" placeholder="Search profiles..." data-role="profile-search" aria-label="Search profiles" />
                        </div>
                        <div class="weirdion-profile-actions">
                            <button class="weirdion-button primary" data-action="new" title="New Profile (Ctrl+N)">
                                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                                    <path d="M7 1V13M1 7H13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                                </svg>
                                New
                            </button>
                            <button class="weirdion-button" data-action="save" title="Save Profile (Ctrl+S)">Save</button>
                        </div>
                        <div class="weirdion-profile-list" data-role="profile-list"></div>
                    </aside>
                    <main class="weirdion-profile-main">
                        <div class="weirdion-profile-form">
                            <div class="weirdion-form-header">
                                <h3 data-role="form-title">Profile Settings</h3>
                                <div class="weirdion-form-actions">
                                    <button class="weirdion-button-icon" data-action="save-as" title="Save As...">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                            <path d="M13 13H3C2.44772 13 2 12.5523 2 12V4C2 3.44772 2.44772 3 3 3H10L14 7V12C14 12.5523 13.5523 13 13 13Z" stroke="currentColor" stroke-width="1.5"/>
                                            <path d="M5 3V7H11" stroke="currentColor" stroke-width="1.5"/>
                                        </svg>
                                    </button>
                                    <button class="weirdion-button-icon danger" data-action="delete" title="Delete Profile">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                            <path d="M3 4H13M5 4V3C5 2.44772 5.44772 2 6 2H10C10.5523 2 11 2.44772 11 3V4M6 7V11M10 7V11M4 4H12V13C12 13.5523 11.5523 14 11 14H5C4.44772 14 4 13.5523 4 13V4Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            <div class="weirdion-form-body">
                                <div class="field">
                                    <label for="profile-name">Profile Name</label>
                                    <input type="text" id="profile-name" data-field="name" required aria-required="true" />
                                </div>
                                <div class="field-group">
                                    <div class="field">
                                        <label for="profile-steps">Steps</label>
                                        <input type="number" id="profile-steps" min="1" max="200" data-field="steps" required aria-required="true" />
                                    </div>
                                    <div class="field">
                                        <label for="profile-cfg">CFG Scale</label>
                                        <input type="number" id="profile-cfg" min="0" max="30" step="0.1" data-field="cfg" required aria-required="true" />
                                    </div>
                                    <div class="field">
                                        <label for="profile-denoise">Denoise</label>
                                        <input type="number" id="profile-denoise" min="0" max="1" step="0.01" data-field="denoise" required aria-required="true" />
                                    </div>
                                    <div class="field">
                                        <label for="profile-clip-skip">Clip Skip</label>
                                        <input type="number" id="profile-clip-skip" min="-12" max="12" step="1" data-field="clip_skip" required aria-required="true" />
                                    </div>
                                </div>
                                <div class="field-group">
                                    <div class="field">
                                        <label for="profile-sampler">Sampler</label>
                                        <input type="text" id="profile-sampler" data-field="sampler" placeholder="e.g., euler_ancestral" />
                                    </div>
                                    <div class="field">
                                        <label for="profile-scheduler">Scheduler</label>
                                        <input type="text" id="profile-scheduler" data-field="scheduler" placeholder="e.g., karras" />
                                    </div>
                                </div>
                                <div class="field field-full">
                                    <label for="profile-note">Notes</label>
                                    <textarea id="profile-note" data-field="note" rows="6" placeholder="Add notes about this profile..."></textarea>
                                </div>
                                <div class="field field-full">
                                    <label>Checkpoint Associations</label>
                                    <div class="weirdion-checkpoint-search">
                                        <input type="text" placeholder="Search checkpoints..." data-role="checkpoint-search" />
                                    </div>
                                    <div class="weirdion-checkpoint-chips" data-role="checkpoint-chips"></div>
                                </div>
                                <div class="weirdion-profile-hint" data-role="profile-hint"></div>
                            </div>
                        </div>
                    </main>
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

        // Keyboard shortcuts
        this.keyHandler = (event) => {
            if (event.key === "Escape") {
                this.close();
                event.preventDefault();
            } else if ((event.ctrlKey || event.metaKey) && event.key === "s") {
                event.preventDefault();
                this._saveProfile(false);
            } else if ((event.ctrlKey || event.metaKey) && event.key === "n") {
                event.preventDefault();
                this._selectProfile("");
            }
        };

        // Profile search
        const profileSearch = this.modal.querySelector('[data-role="profile-search"]');
        if (profileSearch) {
            profileSearch.addEventListener("input", (e) => {
                this.profileSearchQuery = e.target.value.toLowerCase();
                this._renderProfileList();
            });
        }

        // Checkpoint search
        const checkpointSearch = this.modal.querySelector('[data-role="checkpoint-search"]');
        if (checkpointSearch) {
            checkpointSearch.addEventListener("input", (e) => {
                this.checkpointSearchQuery = e.target.value.toLowerCase();
                this._renderCheckpointChips();
            });
        }
    }

    async open() {
        try {
            this.data = await fetchProfiles();
            this.data.profiles = this.data.profiles || {};
            this.data.checkpoint_defaults = this.data.checkpoint_defaults || {};
            this.data.checkpoints = this.data.checkpoints || [];
            this.profileSearchQuery = "";
            this.checkpointSearchQuery = "";
            window.weirdionProfileData = this.data;
            this._render();
            this.overlay.classList.add("is-open");
            this.modal.classList.add("is-open");
            document.addEventListener("keydown", this.keyHandler);
        } catch (error) {
            showToast(error.message || "Failed to open Profile Manager", "error");
        }
    }

    close() {
        this.overlay.classList.remove("is-open");
        this.modal.classList.remove("is-open");
        document.removeEventListener("keydown", this.keyHandler);
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

        // Filter by search query
        const query = this.profileSearchQuery || "";
        const filtered = names.filter((name) => name.toLowerCase().includes(query));

        if (filtered.length === 0) {
            const empty = document.createElement("div");
            empty.className = "weirdion-profile-empty";
            empty.textContent = "No profiles found";
            listEl.appendChild(empty);
            return;
        }

        filtered.forEach((name) => {
            const pill = document.createElement("div");
            pill.className = "weirdion-profile-pill";
            if (name === this.selectedProfile) {
                pill.classList.add("active");
            }

            const nameEl = document.createElement("span");
            nameEl.className = "profile-name";
            nameEl.textContent = name;

            const tagEl = document.createElement("span");
            tagEl.className = "pill-tag";
            tagEl.textContent = name === DEFAULT_PROFILE_NAME ? "default" : "user";

            pill.appendChild(nameEl);
            pill.appendChild(tagEl);
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

        // Filter by search query
        const query = this.checkpointSearchQuery || "";
        const filtered = allNames.filter((name) => name.toLowerCase().includes(query));

        if (filtered.length === 0 && query) {
            const empty = document.createElement("div");
            empty.className = "weirdion-checkpoint-empty";
            empty.textContent = "No checkpoints found";
            chipsEl.appendChild(empty);
            return;
        }

        filtered.forEach((ckpt) => {
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

    const checkpointWidget = node.widgets?.find((w) => w.name === "checkpoint_name" || w.name === "checkpoint");
    const hasCheckpoint = Boolean(checkpointWidget);
    const checkpointName =
        checkpointWidget?.value === "Select Checkpoint" ? "" : checkpointWidget?.value || "";
    const data = window.weirdionProfileData;
    const checkpointChanged = node._weirdionCheckpointName !== checkpointName;
    let baseProfile =
        node._weirdionProfileBase ||
        node._weirdionProfileValue ||
        stripUnsaved(profileWidget.value || DEFAULT_PROFILE_NAME) ||
        DEFAULT_PROFILE_NAME;
    const wasApplying = node._weirdionApplying;
    node._weirdionApplying = true;

    try {
        if (!node._weirdionProfileDirty && checkpointChanged && data && hasCheckpoint) {
            const mapped = data.checkpoint_defaults?.[checkpointName];
            if (mapped && data.profiles?.[mapped]) {
                baseProfile = mapped;
            } else {
                baseProfile = DEFAULT_PROFILE_NAME;
            }
            node._weirdionProfileBase = baseProfile;
        }

        if (!data) {
            profileWidget.options.values = [DEFAULT_PROFILE_NAME];
            profileWidget.value = DEFAULT_PROFILE_NAME;
            return;
        }

        const profiles = data.profiles || {};
        const values = hasCheckpoint
            ? [
                  DEFAULT_PROFILE_NAME,
                  ...Object.keys(profiles).filter((name) =>
                      (profiles[name].checkpoints || []).includes(checkpointName)
                  ),
                  ...Object.keys(profiles).filter(
                      (name) => (profiles[name].checkpoints || []).length === 0
                  ),
              ]
            : [DEFAULT_PROFILE_NAME, ...Object.keys(profiles).sort()];
        let unique = Array.from(new Set(values));

        if (!unique.includes(baseProfile) && baseProfile !== DEFAULT_PROFILE_NAME) {
            unique = [baseProfile, ...unique];
        }

        if (!unique.includes(baseProfile)) {
            baseProfile = DEFAULT_PROFILE_NAME;
        }

        profileWidget.value = baseProfile;
        node._weirdionProfileBase = baseProfile;
        profileWidget.options.values = unique;

        const noteWidget = node.widgets?.find((w) => w.name === "profile_note");
        if (noteWidget) {
            noteWidget.value = resolveProfileNote(data, checkpointName, baseProfile, hasCheckpoint);
        }

        if (!node._weirdionProfileDirty) {
            const profileData = resolveProfileData(data, checkpointName, baseProfile, hasCheckpoint);
            setProfileValues(node, profileData);
        }
    } finally {
        node._weirdionCheckpointName = checkpointName;
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
            PROFILE_NODE_INSTANCES.forEach((node) => syncProfileState(node));
        } catch (error) {
            console.warn("[weirdion] Failed to preload profiles", error);
        }

        window.addEventListener("weirdion:profiles-updated", async () => {
            try {
                window.weirdionProfileData = await fetchProfiles();
                PROFILE_NODE_INSTANCES.forEach((node) => syncProfileState(node));
            } catch (error) {
                console.warn("[weirdion] Failed to refresh profiles", error);
            }
        });
    },

    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (!PROFILE_NODES.includes(nodeData.name)) {
            return;
        }

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated?.apply(this, arguments);

            addProfileNoteWidget(this);
            PROFILE_NODE_INSTANCES.add(this);

            const checkpointWidget = this.widgets?.find((w) => w.name === "checkpoint_name" || w.name === "checkpoint");
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
                    applyProfileFilters(node);
                };
            }

            const profileWidget = this.widgets?.find((w) => w.name === "profile");
            if (profileWidget) {
                configureProfileWidget(this, profileWidget);
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

            const originalConfigure = this.onConfigure;
            this.onConfigure = function () {
                const result = originalConfigure?.apply(this, arguments);
                requestAnimationFrame(() => syncProfileState(this));
                return result;
            };

            const originalResize = this.onResize;
            this.onResize = function () {
                const result = originalResize?.apply(this, arguments);
                updateNoteHeightFromNode(this);
                return result;
            };
            return result;
        };
    },
});
