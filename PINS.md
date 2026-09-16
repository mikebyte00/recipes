# Pins

The catalogue binding every canonical ingredient to a purchasable product. A
Recipe's `ingredient:` key is a key in this file.

Rules live in
[Mint The Pin Catalogue](.scratch/meal-planning-system/issues/11-mint-the-pin-catalogue.md);
the shape in
[How Ingredients Are Named](.scratch/meal-planning-system/issues/04-how-ingredients-are-named.md).
Every row here was confirmed by hand in
[Confirm And Write The Pins](.scratch/meal-planning-system/issues/13-confirm-and-write-the-pins.md),
07 September 2026, and reconciled against the Recipes in
[Normalise Ingredient Units](.scratch/meal-planning-system/issues/12-normalise-ingredient-units.md)
the same day — which merged seven near-duplicate slugs and took `staple` off the
recipe ingredient, leaving the Pin as its only home.

The coverage counts below — the 94-Pin breakdown, [Absences](#absences), and
[Bought, matched nothing](#bought-matched-nothing) — were recounted against the
pool on 09 September 2026, after five Recipes landed and took the corpus to 42.
`pancetta` was pinned directly on 16 September 2026 (see [Absences](#absences)),
taking the catalogue to 88. The 08 September harvest minted six more —
`banana`, `blue-cheese`, `chestnut-mushrooms`, `green-beans`, `milk-chocolate`,
`quorn-pieces` — and added a line number to the existing `tarragon` staple,
taking the catalogue to 94.

## Reading a Pin

| Field | Meaning |
|---|---|
| key | what a Recipe cites — `lower-kebab-case`, matching `ingredient:` |
| `display` | what you read on a shopping list |
| `store` | `waitrose` · `soutars` · `dorset-meats`. Only Waitrose is online |
| `unit` | **how the Recipe measures it.** Recipes must comply; a mismatch is an error at list time |
| `pack` | **how it is sold.** The pack division happens once, here, at list time — never in a Recipe |
| `each_g` | bridges count and mass where a Recipe needs both |
| `search_term` | the harvested product name, **verbatim**. What Waitrose search actually needs |
| `line_number` | the 6-digit Waitrose product id. Absent means never harvested |
| `alternates` | the product this one beat, or an acceptable substitute |
| `staple` | store-cupboard. Recipes call for it, the shopping list leaves it out |
| `confirmed` | a machine proposed it and a human agreed. Consumers filter on this |

## What a Recipe may write

Two rules, and a consumer can check both.

1. **A quantified ingredient uses its Pin's `unit`, exactly.** Any other unit is
   an error at list time, not a conversion to attempt.
2. **A `staple` may omit `qty` and `unit` both** — `{ ingredient: olive-oil }`.
   It never reaches a shopping list, so a number would be invented precision. A
   **non-staple** with no `qty` is an error: a list cannot add a blank.

So the check is: for every ingredient line, either `unit` equals the Pin's
`unit`, or the line has no `qty` and its Pin says `staple: true`. Nothing else
passes. 19 lines across 7 staple slugs currently take the second branch.

**`line_number` is a string.** Leading zeros are significant: `088460` is not
`88460`.

**Unpinned is the absence of a row**, never a row with no product — see
[Absences](#absences). An Unpinned ingredient is flagged for you to add by
hand, and adding it puts it in your order history where the next harvest turns
it into a Pin.

**94 Pins**: 63 with harvested line numbers, 7 counter proteins, 24
store-cupboard staples not yet seen in an order. 24 of the corpus's 118
ingredients have no Pin.

## The catalogue

```yaml
asparagus:
  display: Asparagus
  store: waitrose
  unit: g
  pack: { qty: 200, unit: g }
  search_term: Duchy Organic Asparagus
  line_number: "085532"
  staple: false
  confirmed: true

avocado:
  display: Avocados
  store: waitrose
  unit: each
  pack: { qty: 2, unit: each }
  search_term: Duchy Organic Ripe Avocados
  line_number: "742393"
  alternates: ["Duchy Organic Avocado (046734)"]
  staple: false
  confirmed: true

baby-potatoes:
  display: Baby potatoes
  store: waitrose
  unit: g
  pack: { qty: 750, unit: g }
  search_term: Duchy Organic British Baby Potatoes
  line_number: "816562"
  staple: false
  confirmed: true

balsamic-vinegar:
  display: Balsamic vinegar
  store: waitrose
  unit: g
  staple: true
  confirmed: true

banana:
  display: Bananas
  store: waitrose
  unit: each
  pack: { qty: 6, unit: each }
  search_term: Duchy Organic Fairtrade Bananas
  line_number: "088937"
  staple: false
  confirmed: true

black-beans:
  display: Black beans
  store: waitrose
  unit: can
  pack: { qty: 400, unit: g }
  search_term: Duchy Organic Black Beans in Water
  line_number: "841495"
  staple: false
  confirmed: true

black-pepper:
  display: Black pepper
  store: waitrose
  unit: pinch
  pack: { qty: 100, unit: g }
  search_term: Cooks' Ingredients Black Peppercorns
  line_number: "785492"
  staple: true
  confirmed: true

blue-cheese:
  display: Blue cheese
  store: waitrose
  unit: g
  pack: { qty: 150, unit: g }
  search_term: Saint Agur Blue Cheese
  line_number: "062460"
  staple: false
  confirmed: true

brown-rice:
  display: Brown rice
  store: waitrose
  unit: g
  pack: { qty: 1000, unit: g }
  search_term: Duchy Organic Brown Basmati Rice
  line_number: "086628"
  staple: false
  confirmed: true

butter:
  display: Butter
  store: waitrose
  unit: g
  pack: { qty: 400, unit: g }
  search_term: Yeo Valley Organic Spreadable Blend of Butter and Rapeseed Oil
  line_number: "091728"
  staple: true
  confirmed: true

butter-beans:
  display: Butter beans
  store: waitrose
  unit: g
  pack: { qty: 400, unit: g }
  search_term: Duchy Organic Butter Beans
  line_number: "700325"
  staple: false
  confirmed: true

butternut-squash:
  display: Butternut squash
  store: waitrose
  unit: g
  pack: { qty: 500, unit: g }
  search_term: Cooks' Ingredients Frozen Butternut Vine Squash Chunks
  line_number: "099050"
  staple: false
  confirmed: true

cannellini-beans:
  display: Cannellini beans
  store: waitrose
  unit: g
  pack: { qty: 400, unit: g }
  search_term: Epicure Organic Cannellini Beans
  line_number: "885637"
  alternates: ["Haricot beans"]
  staple: false
  confirmed: true

capers:
  display: Capers
  store: waitrose
  unit: g
  staple: true
  confirmed: true

celery:
  display: Celery
  store: waitrose
  unit: g
  pack: { qty: 400, unit: g }
  search_term: Duchy Organic Celery
  line_number: "085556"
  staple: false
  confirmed: true

cherry-tomatoes:
  display: Cherry tomatoes
  store: waitrose
  unit: g
  pack: { qty: 200, unit: g }
  search_term: Duchy Organic Cherry Vine Tomatoes
  line_number: "097155"
  staple: false
  confirmed: true

chestnut-mushrooms:
  display: Chestnut mushrooms
  store: waitrose
  unit: g
  pack: { qty: 250, unit: g }
  search_term: Duchy Organic British Chestnut Mushrooms
  line_number: "085540"
  staple: false
  confirmed: true

chicken-breast:
  display: Chicken breasts
  store: soutars
  unit: each
  each_g: 160
  staple: false
  confirmed: true

chicken-thighs:
  display: Chicken thighs
  store: soutars
  unit: each
  each_g: 120
  staple: false
  confirmed: true

chickpeas:
  display: Chickpeas
  store: waitrose
  unit: can
  pack: { qty: 410, unit: g }
  search_term: Duchy Organic Chickpeas in Water
  line_number: "813558"
  staple: false
  confirmed: true

chili-flakes:
  display: Chilli flakes
  store: waitrose
  unit: tsp
  staple: true
  confirmed: true

chili-powder:
  display: Chilli powder
  store: waitrose
  unit: tsp
  staple: true
  confirmed: true

cottage-cheese:
  display: Cottage cheese
  store: waitrose
  unit: g
  pack: { qty: 250, unit: g }
  search_term: Longley Farm Yorkshire Natural Cottage Cheese
  line_number: "417999"
  alternates: ["Essential Cottage Cheese Strength 1 (016264)"]
  staple: false
  confirmed: true

courgette:
  display: Courgettes
  store: waitrose
  unit: g
  pack: { qty: 300, unit: g }
  search_term: Duchy Organic Courgettes
  line_number: "520941"
  staple: false
  confirmed: true

curry-powder:
  display: Curry powder
  store: waitrose
  unit: g
  pack: { qty: 95, unit: g }
  search_term: Cooks' Ingredients Medium Curry Powder
  line_number: "515328"
  staple: true
  confirmed: true

dijon-mustard:
  display: Dijon mustard
  store: waitrose
  unit: g
  staple: true
  confirmed: true

dried-herbs:
  display: Dried herbs
  store: waitrose
  unit: g
  alternates: ["Garlic powder"]
  staple: true
  confirmed: true

dried-oregano:
  display: Dried oregano
  store: waitrose
  unit: g
  pack: { qty: 12, unit: g }
  search_term: Cooks' Ingredients Oregano
  line_number: "432563"
  alternates: ["Italian seasoning"]
  staple: true
  confirmed: true

dried-parsley:
  display: Dried parsley
  store: waitrose
  unit: pinch
  staple: true
  confirmed: true

eggs:
  display: Eggs
  store: soutars
  unit: each
  staple: false
  confirmed: true

feta:
  display: Feta
  store: waitrose
  unit: g
  pack: { qty: 200, unit: g }
  search_term: Duchy Organic Greek Feta Cheese Strength 3
  line_number: "888822"
  staple: false
  confirmed: true

garlic-mayonnaise:
  display: Garlic mayonnaise
  store: waitrose
  unit: ml
  pack: { qty: 280, unit: ml }
  search_term: Waitrose Squeezy Garlic Mayonnaise
  line_number: "832208"
  staple: true
  confirmed: true

garlic-powder:
  display: Garlic powder
  store: waitrose
  unit: pinch
  pack: { qty: 52, unit: g }
  search_term: Cooks' Ingredients Garlic Granules
  line_number: "470588"
  staple: true
  confirmed: true

gochujang:
  display: Gochujang (hot honey)
  store: waitrose
  unit: g
  pack: { qty: 105, unit: g }
  search_term: Cooks' Ingredients Hot Honey Gochujang
  line_number: "930008"
  staple: true
  confirmed: true

greek-yogurt:
  display: Greek yogurt
  store: waitrose
  unit: g
  pack: { qty: 950, unit: g }
  search_term: Fage Total 2% Fat Natural Greek Yogurt Large
  line_number: "603600"
  staple: false
  confirmed: true

green-beans:
  display: Green beans
  store: waitrose
  unit: g
  pack: { qty: 225, unit: g }
  search_term: Duchy Organic Green Beans
  line_number: "085542"
  staple: false
  confirmed: true

green-pesto:
  display: Green pesto
  store: waitrose
  unit: g
  pack: { qty: 190, unit: g }
  search_term: No.1 Italian Pesto Alla Genovese
  line_number: "090431"
  staple: false
  confirmed: true

harissa-paste:
  display: Harissa paste
  store: waitrose
  unit: g
  staple: true
  confirmed: true

honey:
  display: Honey
  store: soutars
  unit: g
  alternates: ["Maple syrup"]
  staple: true
  confirmed: true

hot-sauce:
  display: Hot sauce
  store: waitrose
  unit: g
  staple: true
  confirmed: true

lemon:
  display: Lemons
  store: waitrose
  unit: each
  pack: { qty: 3, unit: each }
  search_term: Duchy Organic Unwaxed Lemons
  line_number: "088911"
  alternates: ["Cooks' Ingredients Unwaxed Lemons (088460)"]
  staple: false
  confirmed: true

lemon-sole-fillets:
  display: Lemon sole fillets
  store: waitrose
  unit: g
  pack: { qty: 270, unit: g }
  search_term: Waitrose 2 Lightly Dusted Lemon Sole Fillets
  line_number: "706832"
  staple: false
  confirmed: true

lemon-sole-goujons:
  display: Lemon sole goujons
  store: waitrose
  unit: box
  pack: { qty: 220, unit: g }
  search_term: Waitrose Frozen Breaded Atlantic Lemon Sole Goujons
  line_number: "411864"
  staple: false
  confirmed: true

lentils:
  display: Lentils, pre-cooked
  store: waitrose
  unit: g
  pack: { qty: 250, unit: g }
  search_term: Merchant Gourmet Puy & Green Lentils
  line_number: "054268"
  alternates: ["Epicure Organic Bijoux Verts Lentils (054002)"]
  staple: false
  confirmed: true

light-cream-cheese:
  display: Light cream cheese
  store: waitrose
  unit: g
  pack: { qty: 250, unit: g }
  search_term: Duchy Organic Soft Cheese Strength 1
  line_number: "563021"
  alternates: ["Quark"]
  staple: false
  confirmed: true

lime:
  display: Limes
  store: waitrose
  unit: each
  pack: { qty: 4, unit: each }
  search_term: Cooks' Ingredients Unwaxed Limes
  line_number: "011269"
  staple: false
  confirmed: true

milk-chocolate:
  display: Milk chocolate
  store: waitrose
  unit: g
  pack: { qty: 90, unit: g }
  search_term: Green & Black's Organic 37% Milk Chocolate Bar
  line_number: "045527"
  staple: false
  confirmed: true

oat-milk:
  display: Oat milk
  store: waitrose
  unit: ml
  pack: { qty: 1000, unit: ml }
  search_term: MOMA Organic Oat Barista
  line_number: "662470"
  staple: false
  confirmed: true

oil-spray:
  display: Oil spray
  store: waitrose
  unit: g
  staple: true
  confirmed: true

olive-oil:
  display: Olive oil
  store: waitrose
  unit: g
  staple: true
  confirmed: true

pak-choi:
  display: Pak choi
  store: waitrose
  unit: g
  pack: { qty: 250, unit: g }
  search_term: Waitrose Green Pak Choi
  line_number: "086170"
  staple: false
  confirmed: true

pancetta:
  display: Pancetta
  store: soutars
  unit: g
  staple: false
  confirmed: true

parmesan:
  display: Parmesan
  store: waitrose
  unit: g
  pack: { qty: 200, unit: g }
  search_term: Duchy Organic Parmigiano Reggiano DOP
  line_number: "504844"
  staple: false
  confirmed: true

passata:
  display: Passata
  store: waitrose
  unit: g
  pack: { qty: 680, unit: g }
  search_term: Duchy Organic Passata
  line_number: "828996"
  staple: false
  confirmed: true

peanut-butter:
  display: Peanut butter
  store: waitrose
  unit: g
  staple: true
  confirmed: true

pearl-barley:
  display: Pearl barley
  store: waitrose
  unit: g
  pack: { qty: 500, unit: g }
  search_term: Waitrose Pearl Barley
  line_number: "055532"
  staple: false
  confirmed: true

peri-peri-mayonnaise:
  display: Peri peri mayonnaise
  store: waitrose
  unit: ml
  pack: { qty: 280, unit: ml }
  search_term: Waitrose Squeezy Piri Piri Mayonnaise
  line_number: "563763"
  staple: true
  confirmed: true

peri-peri-sauce:
  display: Peri peri sauce
  store: waitrose
  unit: tbsp
  staple: true
  confirmed: true

pine-nuts:
  display: Pine nuts
  store: waitrose
  unit: g
  pack: { qty: 100, unit: g }
  search_term: Waitrose Duchy Organic Pine Kernels
  line_number: "520168"
  staple: false
  confirmed: true

potatoes:
  display: Potatoes
  store: waitrose
  unit: g
  pack: { qty: 1500, unit: g }
  search_term: Duchy Organic British Potatoes
  line_number: "085504"
  staple: false
  confirmed: true

quinoa:
  display: Quinoa
  store: waitrose
  unit: pack
  pack: { qty: 250, unit: g }
  search_term: Merchant Gourmet Red & White Quinoa
  line_number: "544453"
  staple: false
  confirmed: true

quorn-pieces:
  display: Quorn pieces
  store: waitrose
  unit: g
  pack: { qty: 300, unit: g }
  search_term: Quorn Vegetarian Pieces
  line_number: "441467"
  staple: false
  confirmed: true

ras-el-hanout:
  display: Ras el hanout
  store: waitrose
  unit: g
  pack: { qty: 50, unit: g }
  search_term: Cooks' Ingredients Ras el Hanout
  line_number: "682477"
  alternates: ["Moroccan spice blend"]
  staple: true
  confirmed: true

raspberries:
  display: Raspberries
  store: waitrose
  unit: g
  pack: { qty: 125, unit: g }
  search_term: Duchy Organic Raspberries
  line_number: "096831"
  staple: false
  confirmed: true

red-pesto:
  display: Red pesto
  store: waitrose
  unit: g
  pack: { qty: 190, unit: g }
  search_term: No.1 Calabrian Chilli, Red Pepper & Almond Pesto
  line_number: "542712"
  staple: false
  confirmed: true

rocket:
  display: Babyleaf & rocket salad
  store: waitrose
  unit: g
  pack: { qty: 100, unit: g }
  search_term: Duchy Organic Babyleaf & Rocket Salad
  line_number: "483605"
  staple: false
  confirmed: true

rosemary:
  display: Rosemary
  store: waitrose
  unit: pinch
  pack: { qty: 22, unit: g }
  search_term: Cooks' Ingredients Rosemary
  line_number: "795920"
  staple: true
  confirmed: true

salmon:
  display: Salmon fillets
  store: dorset-meats
  unit: fillets
  each_g: 150
  alternates: ["Chalk stream trout"]
  staple: false
  confirmed: true

salt:
  display: Salt
  store: waitrose
  unit: pinch
  staple: true
  confirmed: true

sea-salt-flakes:
  display: Sea salt flakes
  store: waitrose
  unit: pinch
  staple: true
  confirmed: true

sesame-oil:
  display: Sesame oil
  store: waitrose
  unit: g
  staple: true
  confirmed: true

sirloin-steak:
  display: Sirloin steak
  store: soutars
  unit: g
  each_g: 150
  staple: false
  confirmed: true

smoked-paprika:
  display: Smoked paprika
  store: waitrose
  unit: g
  pack: { qty: 40, unit: g }
  search_term: Cooks' Ingredients Smoked Paprika
  line_number: "700918"
  staple: true
  confirmed: true

sourdough:
  display: Bread
  store: waitrose
  unit: slices
  pack: { qty: 12, unit: slices }
  search_term: Light Rye Boule
  line_number: "841175"
  staple: false
  confirmed: true

soy-sauce:
  display: Soy sauce
  store: waitrose
  unit: g
  alternates: ["Tamari"]
  staple: true
  confirmed: true

spinach:
  display: Spinach
  store: waitrose
  unit: g
  pack: { qty: 200, unit: g }
  search_term: Duchy Organic Spinach
  line_number: "022524"
  staple: false
  confirmed: true

spring-onions:
  display: Spring onions
  store: waitrose
  unit: g
  pack: { qty: 100, unit: g }
  search_term: Duchy Organic Salad Onions Bunch
  line_number: "086479"
  staple: false
  confirmed: true

sugar-snap-peas:
  display: Sugar snap peas
  store: waitrose
  unit: g
  pack: { qty: 160, unit: g }
  search_term: Waitrose Baby Sugar Snaps
  line_number: "024418"
  staple: false
  confirmed: true

sweetcorn:
  display: Sweetcorn
  store: waitrose
  unit: can
  pack: { qty: 150, unit: g }
  search_term: Waitrose Duchy Organic Sweetcorn
  line_number: "987154"
  staple: false
  confirmed: true

tarragon:
  display: Tarragon
  store: waitrose
  unit: g
  pack: { qty: 11, unit: g }
  search_term: Cooks' Ingredients Tarragon
  line_number: "455285"
  staple: true
  confirmed: true

tartare-sauce:
  display: Tartare sauce
  store: waitrose
  unit: g
  pack: { qty: 290, unit: g }
  search_term: Essential Tartare Sauce
  line_number: "034638"
  alternates: ["Waitrose Tartare Sauce (933476)"]
  staple: false
  confirmed: true

tofu:
  display: Tofu
  store: waitrose
  unit: pack
  pack: { qty: 200, unit: g }
  search_term: Taifun Organic Smoked Tofu
  line_number: "498037"
  staple: false
  confirmed: true

tomato-puree:
  display: Tomato puree
  store: waitrose
  unit: g
  pack: { qty: 200, unit: g }
  search_term: Mr Organic Tomato Puree
  line_number: "986590"
  staple: true
  confirmed: true

truffle-oil:
  display: Truffle oil
  store: waitrose
  unit: g
  staple: true
  confirmed: true

vanilla-bean-paste:
  display: Vanilla bean paste
  store: waitrose
  unit: g
  staple: true
  confirmed: true

vanilla-extract:
  display: Vanilla extract
  store: waitrose
  unit: g
  staple: true
  confirmed: true

vegetable-stock:
  display: Vegetable stock
  store: waitrose
  unit: ml
  staple: true
  confirmed: true

vegetarian-sausage:
  display: Vegetarian sausages
  store: waitrose
  unit: each
  pack: { qty: 8, unit: each }
  search_term: Richmond 8 Vegan Meat Free Sausages
  line_number: "551047"
  staple: false
  confirmed: true

white-chocolate:
  display: White chocolate
  store: waitrose
  unit: g
  pack: { qty: 90, unit: g }
  search_term: Green & Black's Organic 30% White Chocolate Bar
  line_number: "032753"
  alternates: ["Cooks' Ingredients White Chocolate (746489)"]
  staple: false
  confirmed: true

white-fish:
  display: White fish fillets
  store: dorset-meats
  unit: fillets
  each_g: 150
  alternates: ["Bream", "Bass"]
  staple: false
  confirmed: true

white-miso-paste:
  display: White miso paste
  store: waitrose
  unit: g
  staple: true
  confirmed: true

wholewheat-penne:
  display: Wholewheat penne
  store: waitrose
  unit: g
  pack: { qty: 500, unit: g }
  search_term: Waitrose Wholewheat Penne
  line_number: "526234"
  staple: false
  confirmed: true

wholewheat-spaghetti:
  display: Wholewheat spaghetti
  store: waitrose
  unit: g
  pack: { qty: 500, unit: g }
  search_term: Waitrose Wholewheat Spaghetti
  line_number: "648428"
  staple: false
  confirmed: true

worcestershire-sauce:
  display: Worcestershire sauce
  store: waitrose
  unit: g
  staple: true
  confirmed: true
```

## Absences

The 24 ingredients with no Pin, and why. Recorded here so the catalogue's
coverage is checkable rather than assumed. **This list is the Unpinned flag**:
an ingredient here is added to the order by hand, and buying it once puts it in
the order history where the next harvest turns it into a Pin.

`pancetta` was pinned directly on 16 September 2026 — Soutars, not Waitrose, so
it would never have surfaced through a harvest. Recorded here rather than in
the counts below, since it broke the assumption the rest of this section rests
on.

The 08 September harvest resolved six of these: `banana`, `blue-cheese`,
`chestnut-mushrooms`, `green-beans`, `milk-chocolate` all matched a harvested
product and are now Pins; `quorn-pieces` arrived with three new Recipes and
matched Quorn Vegetarian Pieces (441467) in the same order.

**Never harvested (20)** — real shopping items absent from the four captured
orders. Each will Pin itself on the next harvest after you buy it.

- `burger-buns` · `flaked-almonds` · `halloumi` · `lettuce` · `parsley` ·
  `pineapple` · `red-onion` · `strawberries` · `waffle-fries` ·
  `wholewheat-linguine` · `chilli-oil` · `cinnamon` · `coconut-milk` ·
  `jerk-seasoning` · `kidney-beans` · `marmalade` · `rice-vinegar` ·
  `spring-onion` · `sweetheart-cabbage` · `peas`

Four of those — `chilli-oil`, `cinnamon`, `jerk-seasoning`, `rice-vinegar` —
read like store cupboard, and would likely mint as staples. Likely is not
confirmed, so they sit here until a harvest and a human say otherwise.

**Fresh, and deliberately not stapled (3)**

- `garlic` · `ginger` · `black-olives` — cupboard-adjacent but genuinely
  perishable, so they belong on a shopping list. No product harvested yet.

**Harvested, not yet minted (1)**

- `blueberries` (Duchy Organic Blueberries, 088973, 31 August)

The ordinary case running backwards: the product was already in the order
history, and the ingredient arrived afterwards with the yogurt pots. A harvest
proposes; a human confirms. Until someone works
[Orders/HARVEST.md](Orders/HARVEST.md) steps 6-9 over it, it has no row, so it
stays on the Unpinned flag and gets added by hand.

## Bought, matched nothing

26 of the 95 harvested products bind to no Pin. Mostly evidence rather than
candidates — matching is slug-driven, so these were never proposed.

Household and personal (9): three cleaning and laundry lines, four paper/bin
lines from the 08 September order, one personal-care refill, one supplement.
Not named here — this file is public, and the page redacts the whole
personal-care category, so listing the products in prose would undo that. The
order files on disk have them.

Groceries outside the recipe corpus (15): grapes · kiwi · carrots · peppers ·
cucumber · radish · watercress · pumpkin seeds · plum tomatoes · blackeye
beans · beef bone broth · chimichurri marinade · tomato salsa dip · Cooks'
Ingredients Basil · **Tenderstem broccoli**.

Chocolate (1): Cooks' Ingredients Belgian Dark Chocolate. The only chocolates
in the order history are dark, milk (now Pinned) and white — this one may well
be what the strawberry pots actually use, but swapping a stated ingredient for
a different one on a hunch is exactly what `confirmed` exists to prevent.

Candidates, not evidence (1): blueberries — answers a corpus ingredient and is
listed under [Absences](#absences) awaiting a minted Pin.

**Tenderstem broccoli** is worth a second look — 200g, bought twice, and no
Recipe in the corpus uses it. That reads like a dinner side you cook regularly
and never wrote down.
