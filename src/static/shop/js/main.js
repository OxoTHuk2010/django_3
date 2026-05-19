document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".accordion-title").forEach((button) => {
        button.addEventListener("click", () => {
            button.closest(".accordion-item")?.classList.toggle("active");
        });
    });

    document.querySelectorAll("[data-quantity-form]").forEach((form) => {
        const input = form.querySelector(".quantity-input");
        if (!input) return;

        const clamp = (value) => {
            const min = Number(input.min || 1);
            const max = input.max ? Number(input.max) : Number.MAX_SAFE_INTEGER;
            return Math.min(Math.max(value, min), max);
        };

        form.querySelectorAll("[data-action]").forEach((button) => {
            button.addEventListener("click", () => {
                const current = Number(input.value || input.min || 1);
                const next = button.dataset.action === "increase" ? current + 1 : current - 1;
                input.value = String(clamp(next));
            });
        });
    });

    document.querySelectorAll(".catalog-filter-form input[type='radio']").forEach((input) => {
        input.addEventListener("change", () => {
            input.form?.submit();
        });
    });
});
