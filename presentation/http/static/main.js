document.addEventListener("DOMContentLoaded", () => {
    const endpointMap = getEndpointMap();
    if (endpointMap === null)
        return;

    const eventSource = getEventSource(endpointMap);

    setupCommandButtons(endpointMap);
    setupStateIndicator(endpointMap, eventSource);
    setupConfigEditor(endpointMap, eventSource);
    setupLogViewer(endpointMap, eventSource);
});

function getEndpointMap() {
    const endpointMapScript = document.getElementById("endpoint-map");
    if (endpointMapScript === null) {
        console.error("cannot find endpoint map element");
        return null;
    }

    try {
        return JSON.parse(endpointMapScript.textContent);
    } catch (err) {
        console.error("error parsing endpoint map:", err);
        return null;
    }
}

function getEventSource(endpointMap) {
    const eventSource = new EventSource(endpointMap["events.stream_events"].url);
    eventSource.onerror = (err) => console.error("error in event source events.stream_events:", err);
    return eventSource;
}

function setupCommandButtons(endpointMap) {
    const buttons = {
        "open-button": "command.send_open",
        "close-button": "command.send_close",
        "stop-button": "command.send_stop",
    };

    for (const [id, name] of Object.entries(buttons)) {
        const button = document.getElementById(id);
        if (button === null) {
            console.warn("cannot find log viewer element:", id);
            continue;
        }

        button.addEventListener("click", async () => {
            try {
                const endpoint = endpointMap[name];
                await fetch(endpoint.url, { method: endpoint.method });
            } catch (err) {
                console.error(`error fetching ${name}:`, err);
            }
        });
    }
}

function setupStateIndicator(endpointMap, eventSource) {
    const stateContainer = document.getElementById("cover-state-container");

    if (stateContainer === null) {
        console.error("cannot find state indicator element");
        return;
    }

    const fetchState = async () => {
        try {
            const endpoint = endpointMap["status.view_status"];
            const res = await fetch(endpoint.url, { method: endpoint.method });
            if (!res.ok) {
                console.error("unexpected response from log.view_log");
                return
            }

            const data = await res.json();
            stateContainer.textContent = data.state;
        } catch (err) {
            console.error("error fetching status.view_status:", err);
        }
    };

    eventSource.addEventListener("state", evt => {
        stateContainer.textContent = evt.data;
    });

    fetchState();
}

function setupConfigEditor(endpointMap, eventSource) {
    const configSchemaScript = document.getElementById("config-schema");
    const formContainer = document.getElementById("config-form-container");
    const saveButton = document.getElementById("config-save-btn");
    const resetButton = document.getElementById("config-reset-btn");

    if (configSchemaScript === null ||
        formContainer === null ||
        saveButton === null ||
        resetButton === null) {
        console.error("cannot find config editor element(s)");
        return;
    }

    let configSchema;
    try {
        configSchema = JSON.parse(configSchemaScript.textContent);
    } catch (err) {
        console.error("error parsing config schema:", err);
        return;
    }

    let config = {};

    const getConfigValue = (path) => {
        const parts = path.split(".");
        let current = config;

        for (const part of parts) {
            if (current === undefined || current === null)
                return undefined;

            current = current[part];
        }

        return current;
    }

    const setConfigValue = (path, value) => {
        const parts = path.split(".");
        let current = config;

        for (const part of parts.slice(0, -1)) {
            if (!(part in current) ||
                current[part] === null ||
                current[part] === undefined ||
                typeof current[part] !== "object") {
                current[part] = {};
            }

            current = current[part];
        }

        current[parts.pop()] = value;
    }

    const renderControl = (labelText, initialValue, type, group, options) => {
        const id = `id-${Math.random().toString(36).substring(2)}`;

        const div = group.appendChild(document.createElement("div"));
        div.className = "control";

        const label = div.appendChild(document.createElement("label"));
        label.htmlFor = id;
        label.textContent = labelText
            .split("_")
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");

        if (type === "select") {
            const select = div.appendChild(document.createElement("select"));
            select.id = id;

            options.forEach(opt => {
                const option = select.appendChild(document.createElement("option"));
                option.textContent = opt;
                option.value = opt;
                if (opt === initialValue) option.selected = true;
            });

            return select;
        } else {
            const input = div.appendChild(document.createElement("input"));
            input.id = id;
            input.type = type;

            if (type === "checkbox") {
                input.checked = initialValue;
            } else {
                input.value = initialValue;
            }

            return input;
        }
    };

    const renderProperties = (props, parentPath, group) => {
        for (const prop of props) {
            const path = `${parentPath}.${prop.name}`;
            const value = getConfigValue(path) ?? prop.default;

            if (prop.type === "boolean") {

                const input = renderControl(prop.name, value, "checkbox", group);
                input.addEventListener("change", () => setConfigValue(path, input.checked));
            }

            if (prop.type === "integer" || prop.type === "float") {
                const input = renderControl(prop.name, value, "number", group);
                input.step = prop.type === "integer" ? "1" : "any";
                input.addEventListener("change", () => {
                    const parsed = prop.type === "integer" ? parseInt(input.value, 10) : parseFloat(input.value);
                    if (!isNaN(parsed)) setConfigValue(path, parsed);
                });
            }

            if (prop.type === "string") {
                const input = renderControl(prop.name, value, "text", group);
                input.addEventListener("change", () => setConfigValue(path, input.value));
            }

            if (prop.type === "list") {
                const input = renderControl(prop.name, value.join(", "), "text", group);
                input.addEventListener("change", () => setConfigValue(path, input.value
                    .split(",")
                    .map(item => item.trim())
                    .filter(item => item !== ""))
                );
            }

            if (prop.type === "enum") {
                const select = renderControl(prop.name, value, "select", group, prop.variants);
                select.addEventListener("change", () => setConfigValue(path, select.value));
            }
        }
    };

    const render = () => {
        formContainer.innerHTML = "";

        for (const entry of configSchema) {
            const fieldset = formContainer.appendChild(document.createElement("fieldset"));
            fieldset.className = "control-group";

            const legend = fieldset.appendChild(document.createElement("legend"));
            legend.textContent = entry.name.replace(/[\._]/g, " ").toUpperCase();

            if (Array.isArray(entry.properties)) {
                renderProperties(entry.properties, entry.name, fieldset);
            } else {
                const currentConfig = getConfigValue(entry.name) ?? {};

                let currentType;
                for (const [type, props] of Object.entries(entry.properties)) {
                    if (props.length !== Object.keys(currentConfig).length)
                        continue;

                    if (!props.every(p => p.name in currentConfig))
                        continue;

                    if (!props.every(p => p.type !== "constant" || currentConfig[p.name] === p.default))
                        continue;

                    currentType = type;
                    break;
                }

                const select = renderControl("type", currentType, "select", fieldset, Object.keys(entry.properties));
                select.addEventListener("change", () => {
                    setConfigValue(entry.name, entry.properties[select.value].reduce((acc, p) => {
                        acc[p.name] = p.default;
                        return acc;
                    }, {}));
                    render();
                });

                renderProperties(entry.properties[currentType], entry.name, fieldset);
            }
        }
    };

    const saveConfig = async () => {
        try {
            const endpoint = endpointMap["config.change_config"];
            const res = await fetch(endpoint.url, {
                method: endpoint.method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(config)
            });

            if (!res.ok)
                console.error("unexpected response from config.change_config");
        } catch (err) {
            console.error("error fetching config.change_config:", err);
        }
    };

    const fetchConfig = async () => {
        try {
            const endpoint = endpointMap["config.view_config"];
            const res = await fetch(endpoint.url, { method: endpoint.method });
            if (!res.ok) {
                console.error("unexpected response from config.view_config");
                return;
            }

            const data = await res.json();
            config = data;
            render();
        } catch (err) {
            console.error("error fetching config.view_config:", err);
        }
    };

    saveButton.addEventListener("click", saveConfig);
    resetButton.addEventListener("click", fetchConfig);
    eventSource.addEventListener("config", fetchConfig);

    fetchConfig();
}

function setupLogViewer(endpointMap, eventSource) {
    const refreshButton = document.getElementById("log-refresh-button");
    const lineLimitField = document.getElementById("log-line-limit-field");
    const outputContainer = document.getElementById("log-output-container");

    if (refreshButton === null ||
        lineLimitField === null ||
        outputContainer === null) {
        console.error("cannot find log viewer element(s)");
        return;
    }

    const getLineLimit = () => {
        const limit = Math.max(0, parseInt(lineLimitField.value || "0", 10));
        if (isNaN(limit))
            return 0;

        return limit;
    };

    const fetchLogs = async () => {
        try {
            const endpoint = endpointMap["log.view_log"];
            const res = await fetch(endpoint.url + `?lines=${getLineLimit()}`, { method: endpoint.method });
            if (!res.ok) {
                console.error("unexpected response from log.view_log");
                return
            }

            outputContainer.textContent = (await res.text())
                .split("\n")
                .reverse()
                .join("\n");
        } catch (err) {
            console.error("error fetching log.view_log:", err);
        }
    };

    refreshButton.addEventListener("click", fetchLogs);
    lineLimitField.addEventListener("change", fetchLogs);

    eventSource.addEventListener("log", (evt) => {
        outputContainer.textContent = outputContainer.textContent
            .split("\n")
            .reverse()
            .concat(evt.data)
            .slice(-getLineLimit())
            .reverse()
            .join("\n");
    });

    fetchLogs();
}
