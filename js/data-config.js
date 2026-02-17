/**
 * Data Source Configuration
 * Supports two GitHub data sources:
 * - remote: current repository data branch
 * - local:  personal repository data branch
 */

const DATA_CONFIG = {
    /**
     * GitHub repository owner (username)
     * This will be replaced during GitHub Actions workflow execution
     */
    repoOwner: 'dw-dengwei',

    /**
     * GitHub repository name
     * This will be replaced during GitHub Actions workflow execution
     */
    repoName: 'daily-arXiv-ai-enhanced',

    /**
     * Data branch name
     * Default: 'data'
     */
    dataBranch: 'data',

    /**
     * Data source switch mode
     * - remote: fetch from raw.githubusercontent.com
     * - local: fetch from personal GitHub data branch
     */
    sourceMode: 'local',
    sourceModeStorageKey: 'arxiv_data_source_mode',
    defaultSourceMode: 'local',

    /**
     * Personal repository data source (used when sourceMode is local)
     */
    localRepoOwner: 'wangtianci2004',
    localRepoName: 'daily-arXiv-ai-enhanced',
    localDataBranch: 'data',

    normalizeMode: function(mode) {
        const normalized = String(mode || '').trim().toLowerCase();
        return normalized === 'local' ? 'local' : 'remote';
    },

    getModeFromQuery: function() {
        try {
            const params = new URLSearchParams(window.location.search);
            const queryMode = params.get('dataSource') || params.get('source');
            return queryMode ? this.normalizeMode(queryMode) : null;
        } catch (error) {
            return null;
        }
    },

    loadSourceMode: function() {
        const queryMode = this.getModeFromQuery();
        if (queryMode) {
            this.sourceMode = queryMode;
            return this.sourceMode;
        }

        try {
            const storedMode = localStorage.getItem(this.sourceModeStorageKey);
            this.sourceMode = this.normalizeMode(storedMode || this.defaultSourceMode);
        } catch (error) {
            this.sourceMode = this.defaultSourceMode;
        }

        return this.sourceMode;
    },

    getSourceMode: function() {
        return this.sourceMode || this.loadSourceMode();
    },

    isLocalMode: function() {
        return this.getSourceMode() === 'local';
    },

    setSourceMode: function(mode) {
        const nextMode = this.normalizeMode(mode);
        this.sourceMode = nextMode;

        try {
            localStorage.setItem(this.sourceModeStorageKey, nextMode);
        } catch (error) {
            // Ignore storage errors in private mode.
        }

        window.dispatchEvent(
            new CustomEvent('data-source-changed', { detail: { mode: nextMode } })
        );

        return nextMode;
    },

    /**
     * Get the base URL for raw GitHub content from data branch
     * @returns {string} Base URL for raw GitHub content
     */
    getDataBaseUrl: function() {
        if (this.isLocalMode()) {
            return `https://raw.githubusercontent.com/${this.localRepoOwner}/${this.localRepoName}/${this.localDataBranch}`;
        }
        return `https://raw.githubusercontent.com/${this.repoOwner}/${this.repoName}/${this.dataBranch}`;
    },

    /**
     * Get the full URL for a data file
     * @param {string} filePath - Relative path to the data file (e.g., 'data/2025-01-01.jsonl')
     * @returns {string} Full URL to the data file
     */
    getDataUrl: function(filePath) {
        const normalizedPath = String(filePath || '').replace(/^\/+/, '');
        const baseUrl = this.getDataBaseUrl();
        return baseUrl ? `${baseUrl}/${normalizedPath}` : normalizedPath;
    }
};

DATA_CONFIG.loadSourceMode();
