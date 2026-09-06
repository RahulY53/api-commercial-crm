window.apiCommercialUI = {
	escape(value) {
		return $("<div>")
			.text(value == null ? "" : String(value))
			.html();
	},

	link(label, route) {
		if (!label) return "—";
		return `<a href="${this.escape(route)}">${this.escape(label)}</a>`;
	},

	pill(value) {
		return value ? `<span class="api-commercial-pill">${this.escape(value)}</span>` : "—";
	},

	table(columns, rows, label) {
		const tableLabel = label || __("Records");
		if (!rows?.length) {
			return `<div class="api-commercial-card api-commercial-empty" role="status">${this.escape(
				__("No records found.")
			)}</div>`;
		}
		const head = columns
			.map((column) => `<th scope="col">${this.escape(column.label)}</th>`)
			.join("");
		const body = rows
			.map(
				(row) =>
					`<tr>${columns
						.map(
							(column) =>
								`<td>${
									column.render
										? column.render(row)
										: this.escape(row[column.key] ?? "—")
								}</td>`
						)
						.join("")}</tr>`
			)
			.join("");
		return `<div class="api-commercial-card api-commercial-table-region" role="region" aria-label="${this.escape(
			tableLabel
		)}" tabindex="0"><table class="api-commercial-table"><caption class="sr-only">${this.escape(
			tableLabel
		)}</caption><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
	},

	metrics(items) {
		return `<div class="api-commercial-summary">${items
			.map(
				(item) =>
					`<div class="api-commercial-card"><div class="api-commercial-label">${this.escape(
						item.label
					)}</div><div class="api-commercial-metric">${this.escape(
						item.value ?? 0
					)}</div></div>`
			)
			.join("")}</div>`;
	},

	details(items) {
		return `<div class="api-commercial-card api-commercial-detail-grid">${items
			.map(
				(item) =>
					`<div><div class="api-commercial-label">${this.escape(item.label)}</div><div>${
						item.html ?? this.escape(item.value ?? "—")
					}</div></div>`
			)
			.join("")}</div>`;
	},

	message(wrapper, message, kind = "status") {
		const target = $(wrapper).find(".layout-main-section");
		const role = kind === "error" ? "alert" : "status";
		target
			.removeAttr("aria-busy")
			.html(
				`<div class="api-commercial-card api-commercial-empty" role="${role}">${this.escape(
					message
				)}</div>`
			);
	},

	async load(wrapper, method, args, render) {
		const target = $(wrapper).find(".layout-main-section");
		const requestId = (wrapper.apiCommercialRequestId || 0) + 1;
		wrapper.apiCommercialRequestId = requestId;
		target
			.attr("aria-busy", "true")
			.html(
				`<div class="api-commercial-card api-commercial-empty" role="status" aria-live="polite">${this.escape(
					__("Loading…")
				)}</div>`
			);
		try {
			const response = await frappe.call({ method, args: args || {} });
			if (wrapper.apiCommercialRequestId !== requestId) return;
			target.html(`<div class="api-commercial-page">${render(response.message)}</div>`);
		} catch (error) {
			if (wrapper.apiCommercialRequestId !== requestId) return;
			console.error(`Unable to load ${method}`, error);
			this.message(wrapper, __("Unable to load this view."), "error");
		} finally {
			if (wrapper.apiCommercialRequestId === requestId) target.removeAttr("aria-busy");
		}
	},
};
