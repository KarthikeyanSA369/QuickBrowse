/**
 * Browser Profile Manager — frontend application logic.
 *
 * No frameworks: plain fetch() calls against the local Flask API and direct
 * DOM manipulation, matching the project's vanilla JS requirement.
 */
(function () {
  "use strict";

  const BROWSER_LOGOS = {
    chrome: "/static/images/browsers/chrome.svg",
    edge: "/static/images/browsers/edge.svg",
    brave: "/static/images/browsers/brave.svg",
  };

  const BROWSER_LABELS = {
    chrome: "Google Chrome",
    edge: "Microsoft Edge",
    brave: "Brave Browser",
  };

  const state = {
    allProfiles: [],
    filteredProfiles: [],
    activeFilter: "all",
    searchTerm: "",
    selectedIndex: -1,
    permissionGranted: false,
  };

  const els = {
    overlay: document.getElementById("permission-overlay"),
    allowBtn: document.getElementById("permission-allow"),
    denyBtn: document.getElementById("permission-deny"),
    searchInput: document.getElementById("search-input"),
    filters: document.getElementById("filters"),
    grid: document.getElementById("profile-grid"),
    emptyState: document.getElementById("empty-state"),
    emptyStateMessage: document.getElementById("empty-state-message"),
    emptyStateAction: document.getElementById("empty-state-action"),
    refreshBtn: document.getElementById("refresh-btn"),
    toastContainer: document.getElementById("toast-container"),
    cardTemplate: document.getElementById("profile-card-template"),
  };

  // ---------------------------------------------------------------------
  // API helpers
  // ---------------------------------------------------------------------
  async function apiGet(path) {
    const res = await fetch(path);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Request failed: ${path}`);
    return data;
  }

  async function apiPost(path, body) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Request failed: ${path}`);
    return data;
  }

  // ---------------------------------------------------------------------
  // Toasts
  // ---------------------------------------------------------------------
  function showToast(message, type) {
    const toast = document.createElement("div");
    toast.className = `toast ${type || ""}`.trim();
    toast.textContent = message;
    els.toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 200ms ease";
      setTimeout(() => toast.remove(), 200);
    }, 3200);
  }

  // ---------------------------------------------------------------------
  // Permission flow
  // ---------------------------------------------------------------------
  async function initPermission() {
    try {
      const state_ = await apiGet("/api/permission");
      if (!state_.decided) {
        els.overlay.hidden = false;
        return false;
      }
      state.permissionGranted = !!state_.granted;
      return state.permissionGranted;
    } catch (err) {
      showToast(err.message, "error");
      return false;
    }
  }

  async function decidePermission(granted) {
    try {
      await apiPost("/api/permission", { granted });
      state.permissionGranted = granted;
      els.overlay.hidden = true;
      if (granted) {
        loadProfiles();
      } else {
        renderEmptyState(true);
      }
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  els.allowBtn.addEventListener("click", () => decidePermission(true));
  els.denyBtn.addEventListener("click", () => decidePermission(false));
  els.emptyStateAction.addEventListener("click", () => {
    els.overlay.hidden = true;
  });

  // ---------------------------------------------------------------------
  // Filters
  // ---------------------------------------------------------------------
  function renderFilters() {
    const pills = [{ id: "all", label: "All", logo: null }].concat(
      Object.keys(BROWSER_LABELS).map((id) => ({ id, label: BROWSER_LABELS[id], logo: BROWSER_LOGOS[id] }))
    );

    els.filters.innerHTML = "";
    pills.forEach((pill) => {
      const btn = document.createElement("button");
      btn.className = "filter-pill" + (pill.id === state.activeFilter ? " active" : "");
      btn.dataset.filter = pill.id;
      if (pill.logo) {
        const img = document.createElement("img");
        img.src = pill.logo;
        img.alt = "";
        btn.appendChild(img);
      }
      const label = document.createElement("span");
      label.textContent = pill.label;
      btn.appendChild(label);
      btn.addEventListener("click", () => {
        state.activeFilter = pill.id;
        renderFilters();
        applyFilters();
      });
      els.filters.appendChild(btn);
    });
  }

  // ---------------------------------------------------------------------
  // Profile loading & rendering
  // ---------------------------------------------------------------------
  async function loadProfiles() {
    try {
      const data = await apiGet("/api/profiles");
      state.permissionGranted = !!data.permissionGranted;
      if (!state.permissionGranted) {
        renderEmptyState(true);
        return;
      }
      state.allProfiles = data.profiles || [];
      applyFilters();
      requestAnimationFrame(() => {
    els.searchInput.focus();
});
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  function applyFilters() {
    const term = state.searchTerm.trim().toLowerCase();
    state.filteredProfiles = state.allProfiles.filter((profile) => {
      const matchesBrowser = state.activeFilter === "all" || profile.browserId === state.activeFilter;
      if (!matchesBrowser) return false;
      if (!term) return true;
      return (
        profile.name.toLowerCase().includes(term) ||
        profile.accountName.toLowerCase().includes(term) ||
        profile.browserName.toLowerCase().includes(term)
      );
    });
    state.selectedIndex = state.filteredProfiles.length ? 0 : -1;
    renderGrid();
  }

  function initials(name) {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return "?";
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  function renderGrid() {
    els.grid.innerHTML = "";

    if (!state.permissionGranted) {
      renderEmptyState(true);
      return;
    }

    if (!state.filteredProfiles.length) {
      renderEmptyState(false);
      return;
    }

    els.emptyState.hidden = true;

    state.filteredProfiles.forEach((profile, index) => {
      const node = els.cardTemplate.content.firstElementChild.cloneNode(true);
      node.dataset.index = String(index);
      node.dataset.profileId = profile.id;

      const img = node.querySelector(".profile-avatar-img");
      const fallback = node.querySelector(".profile-avatar-fallback");
      fallback.textContent = initials(profile.name);
      img.alt = profile.name;
      img.addEventListener("load", () => img.classList.add("loaded"));
      img.addEventListener("error", () => {
        img.classList.remove("loaded");
        img.style.display = "none";
      });
      img.src = profile.avatarUrl;

      node.querySelector(".profile-name").textContent = profile.name;
      node.querySelector(".profile-account").textContent = profile.accountName;

      const logo = node.querySelector(".profile-browser-logo");
      logo.src = BROWSER_LOGOS[profile.browserId] || "";
      logo.alt = profile.browserName;

      if (index === state.selectedIndex) node.classList.add("selected");

      node.addEventListener("click", () => selectCard(index));
      node.addEventListener("dblclick", () => launchProfile(profile.id));
      node.addEventListener("contextmenu", (evt) => {
        evt.preventDefault();
        openFolder(profile.id);
      });

      els.grid.appendChild(node);
    });
  }

  function renderEmptyState(needsPermission) {
    els.grid.innerHTML = "";
    els.emptyState.hidden = false;
    if (needsPermission) {
      els.emptyStateMessage.textContent =
        "Profile access hasn't been granted yet. Allow access to see your browser profiles.";
      els.emptyStateAction.hidden = false;
    } else {
      els.emptyStateMessage.textContent = "No profiles found for this search or filter.";
      els.emptyStateAction.hidden = true;
    }
  }

  function selectCard(index) {
    state.selectedIndex = index;
    document.querySelectorAll(".profile-card").forEach((card) => {
      card.classList.toggle("selected", Number(card.dataset.index) === index);
    });
  }

  // ---------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------
  async function launchProfile(profileId) {
    try {
      const result = await apiPost("/api/launch", { profileId });
      showToast(result.message, "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function openFolder(profileId) {
    try {
      const result = await apiPost("/api/open-folder", { profileId });
      showToast(result.message, "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

async function refreshProfiles() {
    const wasSearchFocused = document.activeElement === els.searchInput;

    els.refreshBtn.classList.add("spinning");

    try {
        await loadProfiles();
        showToast("Profiles refreshed.", "success");
    } finally {
        setTimeout(() => {
            els.refreshBtn.classList.remove("spinning");

            if (wasSearchFocused) {
                els.searchInput.focus();
            }
        }, 400);
    }
}
  els.refreshBtn.addEventListener("click", refreshProfiles);

  // ---------------------------------------------------------------------
  // Search
  // ---------------------------------------------------------------------
els.searchInput.addEventListener("input", (evt) => {
    state.searchTerm = evt.target.value;
    applyFilters();
});

  // ---------------------------------------------------------------------
  // Keyboard shortcuts
  // ---------------------------------------------------------------------
  document.addEventListener("keydown", (evt) => {
    const isSearchFocused = document.activeElement === els.searchInput;

    if (evt.ctrlKey && evt.key.toLowerCase() === "f") {
      evt.preventDefault();
      els.searchInput.focus();
      els.searchInput.select();
      return;
    }

    if (evt.key === "Escape") {
      if (state.searchTerm) {
        state.searchTerm = "";
        els.searchInput.value = "";
        applyFilters();
      }
      els.searchInput.blur();
      return;
    }

    if (evt.key === "Enter") {
      if (!isSearchFocused && state.selectedIndex >= 0 && state.filteredProfiles[state.selectedIndex]) {
        evt.preventDefault();
        launchProfile(state.filteredProfiles[state.selectedIndex].id);
      } else if (!isSearchFocused) {
        els.searchInput.focus();
      }
      return;
    }

    if (
    isSearchFocused &&
    els.searchInput.value.trim().length > 0
) {
    return;
}

    if (evt.key === "ArrowRight" || evt.key === "ArrowDown") {
      evt.preventDefault();
      if (!state.filteredProfiles.length) return;
      state.selectedIndex = Math.min(state.selectedIndex + 1, state.filteredProfiles.length - 1);
      selectCard(state.selectedIndex);
    } else if (evt.key === "ArrowLeft" || evt.key === "ArrowUp") {
      evt.preventDefault();
      if (!state.filteredProfiles.length) return;
      state.selectedIndex = Math.max(state.selectedIndex - 1, 0);
      selectCard(state.selectedIndex);
    }
  });

  // ---------------------------------------------------------------------
  // Boot
  // ---------------------------------------------------------------------
  (async function init() {
    els.searchInput.disabled = false;
    els.searchInput.readOnly = false;
    renderFilters();
    const granted = await initPermission();
    if (granted) {
      await loadProfiles();
    } else if (state.permissionGranted === false && els.overlay.hidden) {
      renderEmptyState(true);
    }
    
  })();
})();
