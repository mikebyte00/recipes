# Pins

The catalogue binding every canonical ingredient to a purchasable product. A
Recipe's `ingredient:` key is a key in this file.

Rules live in
[Mint The Pin Catalogue](.scratch/meal-planning-system/issues/11-mint-the-pin-catalogue.md);
the shape in
[How Ingredients Are Named](.scratch/meal-planning-system/issues/04-how-ingredients-are-named.md).
Every row here was confirmed by hand in
[Confirm And Write The Pins](.scratch/meal-planning-system/issues/13-confirm-and-write-the-pins.md),
07 September 2026.

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

**`line_number` is a string.** Leading zeros are significant: `088460` is not
`88460`.

**Unpinned is the absence of a row**, never a row with no product — see
[Absences](#absences). An Unpinned ingredient is flagged for you to add by
hand, and adding it puts it in your order history where the next harvest turns
it into a Pin.

**94 Pins**: 62 with harvested line numbers, 7 counter proteins, 25
store-cupboard staples not yet seen in an order. 18 of the corpus's 112
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

baby-spinach:
  display: Baby spinach
  store: waitrose
  unit: g
  pack: { qty: 200, unit: g }
  search_term: Duchy Organic Spinach
  line_number: "022524"
  staple: false
  confirmed: true

balsamic-vinegar:
  display: Balsamic vinegar
  store: waitrose
  unit: g
  staple: true
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
  staple: true
  confirmed: true

dried-italian-herbs:
  display: Dried Italian herbs
  store: waitrose
  unit: g
  staple: true
  confirmed: true

dried-oregano:
  display: Dried oregano
  store: waitrose
  unit: g
  pack: { qty: 12, unit: g }
  search_term: Cooks' Ingredients Oregano
  line_number: "432563"
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
  unit: g
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

lemon-juice:
  display: Lemon juice
  store: waitrose
  unit: g
  pack: { qty: 3, unit: each }
  search_term: Duchy Organic Unwaxed Lemons
  line_number: "088911"
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

lime-juice:
  display: Lime juice
  store: waitrose
  unit: g
  pack: { qty: 4, unit: each }
  search_term: Cooks' Ingredients Unwaxed Limes
  line_number: "011269"
  staple: false
  confirmed: true

mixed-salad-greens:
  display: Mixed salad greens
  store: waitrose
  unit: bag
  pack: { qty: 100, unit: g }
  search_term: Duchy Organic Babyleaf & Rocket Salad
  line_number: "483605"
  staple: false
  confirmed: true

new-potatoes:
  display: New potatoes
  store: waitrose
  unit: g
  pack: { qty: 750, unit: g }
  search_term: Duchy Organic British Baby Potatoes
  line_number: "816562"
  staple: false
  confirmed: true

oat-milk:
  display: Oat milk
  store: waitrose
  unit: g
  pack: { qty: 1, unit: litre }
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
  unit: g
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

ras-el-hanout:
  display: Ras el hanout
  store: waitrose
  unit: g
  pack: { qty: 50, unit: g }
  search_term: Cooks' Ingredients Ras el Hanout
  line_number: "682477"
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
  display: Rocket
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
  search_term: Light Rye Boule
  line_number: "841175"
  staple: false
  confirmed: true

soy-sauce:
  display: Soy sauce
  store: waitrose
  unit: g
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

wholegrain-rice:
  display: Wholegrain rice
  store: waitrose
  unit: g
  pack: { qty: 1000, unit: g }
  search_term: Duchy Organic Brown Basmati Rice
  line_number: "086628"
  staple: false
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

The 18 ingredients with no Pin, and why. Recorded here so the catalogue's
coverage is checkable rather than assumed.

**Not a purchasable thing (1)**

- `water` — `staple: true` in all five uses. A row would say only "do not buy
  this".

**Never harvested (14)** — real shopping items absent from the three captured
orders. Each will Pin itself on the next harvest after you buy it.

- `blue-cheese` (Saint Agur light) · `burger-buns` · `chestnut-mushrooms` ·
  `flaked-almonds` · `green-beans` · `halloumi` · `lettuce` · `parsley` ·
  `pineapple` · `red-onion` · `strawberries` · `waffle-fries` ·
  `wholewheat-linguine` · `milk-chocolate`

`milk-chocolate` is the odd one: the only chocolates in the order history are
dark (789167) and white. The Belgian Dark Chocolate may well be what the
strawberry pots actually use, but swapping a stated ingredient for a different
one on a hunch is exactly what `confirmed` exists to prevent.

**Fresh, and deliberately not stapled (3)**

- `garlic` · `ginger` · `black-olives` — cupboard-adjacent but genuinely
  perishable, so they belong on a shopping list. No product harvested yet.

## Bought, matched nothing

24 of the 86 harvested products bind to no ingredient. Evidence, not candidates
— matching is slug-driven, so these were never proposed.

Household and personal (7): Andrex toilet tissue · Ecover washing liquid ×2 ·
Ecover fabric softener · a personal-care refill · a supplement.

Groceries outside the recipe corpus (17): bananas · blueberries · grapes ·
kiwi · carrots · peppers · cucumber · radish · watercress · pumpkin seeds ·
plum tomatoes · blackeye beans · beef bone broth · chimichurri marinade ·
tomato salsa dip · Cooks' Ingredients Basil · **Tenderstem broccoli**.

**Tenderstem broccoli** is worth a second look — 200g, bought twice, and no
Recipe in the corpus uses it. That reads like a dinner side you cook regularly
and never wrote down.
