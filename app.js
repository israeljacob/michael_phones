const storageKey = "kosher_phone_cart_count";
const grid = document.getElementById("productGrid");
const emptyState = document.getElementById("emptyState");
const cartCountEl = document.getElementById("cartCount");
const menuBtn = document.getElementById("menuBtn");
const mainNav = document.getElementById("mainNav");
const chips = document.querySelectorAll(".filter-chip");
const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");
const brandFilter = document.getElementById("brandFilter");
const priceFilter = document.getElementById("priceFilter");
const sortFilter = document.getElementById("sortFilter");
const leadForm = document.getElementById("leadForm");
const leadStatus = document.getElementById("leadStatus");

let cartCount = Number(localStorage.getItem(storageKey) || 0);
let activeFilter = "כל הדגמים";
let activeQuery = "";
cartCountEl.textContent = cartCount;

function productCard(p) {
  return `
    <article class="card">
      <img src="${p.image}" alt="${p.name}" loading="lazy" />
      <div class="card-body">
        <h3 class="card-title">${p.name}</h3>
        <div class="card-meta">מותג: ${p.brand} | רמת כשרות: ${p.level}</div>
        <div class="price-row">
          <span class="price">₪${Number(p.price).toLocaleString()} <span class="old-price">₪${Number(p.oldPrice).toLocaleString()}</span></span>
          <button class="add-btn" type="button">הוסף לסל</button>
        </div>
      </div>
    </article>`;
}

function selectedPriceRange() {
  const value = priceFilter.value;
  if (!value) return { min: "", max: "" };
  const [min, max] = value.split("-");
  return { min: min || "", max: max || "" };
}

function hydrateBrandOptions(brands) {
  if (!brands || brandFilter.options.length > 1) return;
  brands.forEach((brand) => {
    const option = document.createElement("option");
    option.value = brand;
    option.textContent = brand;
    brandFilter.appendChild(option);
  });
}

async function renderProducts() {
  const params = new URLSearchParams();
  const { min, max } = selectedPriceRange();

  if (activeFilter && activeFilter !== "כל הדגמים") params.set("level", activeFilter);
  if (activeQuery.trim()) params.set("q", activeQuery.trim());
  if (brandFilter.value) params.set("brand", brandFilter.value);
  if (sortFilter.value) params.set("sort", sortFilter.value);
  if (min) params.set("min_price", min);
  if (max) params.set("max_price", max);

  const res = await fetch(`/api/products?${params.toString()}`);
  const data = await res.json();
  const items = data.items || [];

  hydrateBrandOptions(data.brands || []);
  emptyState.hidden = items.length > 0;
  grid.innerHTML = items.map(productCard).join("");

  document.querySelectorAll(".add-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      cartCount += 1;
      cartCountEl.textContent = cartCount;
      localStorage.setItem(storageKey, String(cartCount));
    });
  });
}

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    chips.forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    activeFilter = chip.textContent.trim();
    renderProducts();
  });
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  activeQuery = searchInput.value;
  renderProducts();
});

brandFilter.addEventListener("change", renderProducts);
priceFilter.addEventListener("change", renderProducts);
sortFilter.addEventListener("change", renderProducts);

leadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = document.getElementById("leadName").value.trim();
  const phone = document.getElementById("leadPhone").value.trim();
  const need = document.getElementById("leadNeed").value;

  if (!name || !phone || !need) {
    leadStatus.textContent = "אנא מלאו את כל השדות.";
    return;
  }

  leadStatus.textContent = "שולחים את הבקשה...";

  const res = await fetch("/api/leads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, phone, need }),
  });

  if (!res.ok) {
    leadStatus.textContent = "אירעה שגיאה בשמירת הבקשה. נסו שוב.";
    return;
  }

  leadStatus.textContent = `תודה ${name}, הבקשה נשמרה ונחזור אליך בהקדם.`;
  leadForm.reset();
});

menuBtn.addEventListener("click", () => {
  mainNav.classList.toggle("open");
});

renderProducts();
