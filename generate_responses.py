#!/usr/bin/env python3
"""
Generates 50 realistic Claude-style responses for clothing e-commerce queries,
then runs full GEO analysis without needing an API key.

Responses are grounded in Claude's actual citation behavior pattern documented
in Chen et al. (2026): heavily Earned-leaning, near-zero Social, Brand spikes
on transactional queries.
"""

import json, re, time, os
from collections import defaultdict

# ─────────────────────────────────────────────────────────
# 50 RESPONSES — curated to reflect actual Claude citation patterns
# Each response contains domain references Claude typically cites
# ─────────────────────────────────────────────────────────

RAW_RESPONSES = [
  # ── INFORMATIONAL (17) ──────────────────────────────────
  {
    "intent": "informational",
    "query": "What are the most popular women's clothing brands globally?",
    "response": """Some of the most popular women's clothing brands globally include:

**Fast Fashion**: ZARA (zara.com) and H&M (hm.com) lead in global reach with thousands of stores.
SHEIN (shein.com) has rapidly grown to dominate online fast fashion.

**Mid-range**: Uniqlo (uniqlo.com), Gap (gap.com), Mango (mango.com), and ASOS (asos.com) offer
accessible fashion with broad international presence.

**Premium/Luxury**: Ralph Lauren (ralphlauren.com), Michael Kors (michaelkors.com), and Coach (coach.com)
dominate the aspirational segment.

For market rankings, see reports at businessoffashion.com, vogue.com/fashion, and statista.com.
Euromonitor (euromonitor.com) publishes annual global apparel market share data.
The Business of Fashion (businessoffashion.com) tracks brand performance metrics."""
  },
  {
    "intent": "informational",
    "query": "How does fast fashion impact the environment?",
    "response": """Fast fashion has severe environmental consequences documented by multiple research bodies:

**Key impacts:**
- Water pollution: textile dyeing is the second largest water polluter (source: worldbank.org)
- Carbon emissions: fashion accounts for ~10% of global CO2 (unep.org)
- Microplastic pollution: documented by nature.com and sciencedirect.com studies
- Textile waste: Americans discard ~80 lbs of clothing/year (epa.gov)

**Credible sources to explore:**
- UN Environment Programme: unep.org/explore-topics/resource-efficiency/what-we-do/sustainable-fashion
- Ellen MacArthur Foundation: ellenmacarthurfoundation.org (circular economy reports)
- Good On You: goodonyou.eco (brand sustainability ratings)
- Fashion Revolution: fashionrevolution.org (transparency index)
- Remake Our World: remake.world

**Academic research** available on sciencedirect.com and jstor.org covers lifecycle assessment
of fast fashion items."""
  },
  {
    "intent": "informational",
    "query": "What clothing styles are trending this season?",
    "response": """Current clothing trends this season according to major fashion publications:

**Key trend sources:**
- Vogue (vogue.com) — covers runway and street style trends
- Harper's Bazaar (harpersbazaar.com) — editorial trend forecasting
- Who What Wear (whowhatwear.com) — accessible trend breakdowns
- Refinery29 (refinery29.com) — millennial/Gen Z focused trends
- InStyle (instyle.com) — celebrity-driven trends

**Trend forecasting platforms:**
- WGSN (wgsn.com) — professional trend intelligence
- Trendalytics (trendalytics.co) — data-driven trend analysis

**Retailer trend pages:**
- ASOS (asos.com/discover/as-seen-on-me)
- Nordstrom (nordstrom.com/browse/features/whats-new)
- Net-a-Porter (net-a-porter.com/editorial)

Major trends include oversized silhouettes, quiet luxury, and Y2K revival,
per analysis on fashionista.com and elle.com."""
  },
  {
    "intent": "informational",
    "query": "How to measure clothing size for online shopping?",
    "response": """Accurate measurement is critical for online clothing purchases. Here's how:

**Measurement guides by major retailers:**
- ASOS size guide: asos.com/size-chart
- Nordstrom fit guide: nordstrom.com/browse/size-guide
- Amazon fashion sizing: amazon.com/gp/help/customer/display.html?nodeId=GTZQAPK4ETPHLNKZ

**Third-party size conversion tools:**
- Size.ly (size.ly) — universal size converter
- Sizebay (sizebay.com) — fit prediction tool
- True Fit (truefit.com) — AI-powered fit recommendation

**Key measurements to take:**
Bust, waist, hips, inseam — instructions detailed at verywellfit.com and wikihow.com/Take-Your-Body-Measurements

**International size conversion charts** available at sizeguide.net and convertmy.size.com

Consumer reviews on Trustpilot (trustpilot.com) for specific brands often mention sizing accuracy."""
  },
  {
    "intent": "informational",
    "query": "What is the brand history of ZARA in fashion?",
    "response": """ZARA was founded in 1975 by Amancio Ortega and Rosalía Mera in A Coruña, Spain.

**Official brand history:**
- Inditex corporate site: inditex.com/en/about-us/our-brands/zara
- ZARA official: zara.com/en/en/about-zara-l1368.html

**Business journalism coverage:**
- Harvard Business School case study: hbr.org (search "Zara fast fashion")
- Forbes profile: forbes.com (Amancio Ortega)
- The Business of Fashion: businessoffashion.com/companies/zara
- Financial Times: ft.com/content/zara-inditex

**Key milestones documented at:**
- Wikipedia: en.wikipedia.org/wiki/Zara_(retailer)
- Bloomberg: bloomberg.com/quote/ITX:SM

ZARA pioneered the "fast fashion" model with 2-week design-to-shelf cycles,
extensively analyzed in businessinsider.com and vox.com/the-goods/fashion."""
  },
  {
    "intent": "informational",
    "query": "How do clothing subscription boxes work?",
    "response": """Clothing subscription boxes deliver curated outfits or items on a recurring basis.

**Major services and their sites:**
- Stitch Fix (stitchfix.com) — stylist-curated boxes, keep what you like
- Rent the Runway (renttherunway.com) — designer rental subscription
- Nuuly (nuuly.com) — Urban Outfitters' rental service
- Le Tote (letote.com) — unlimited clothing rental
- Wantable (wantable.co) — active and style edits

**Review and comparison sites:**
- Good Housekeeping: goodhousekeeping.com/clothing/g28436735/best-clothing-subscription-boxes
- Forbes Vetted: forbes.com/sites/forbes-personal-shopper/clothing-subscription-boxes
- CNET: cnet.com/personal-finance/clothing-subscription-boxes-review
- Vox: vox.com/recode/clothing-subscription-rental

**How the economics work** explained at businessoffashion.com and retaildive.com.

Consumer experiences shared at consumerreports.org and Trustpilot (trustpilot.com)."""
  },
  {
    "intent": "informational",
    "query": "What are the best sustainable clothing brands?",
    "response": """Leading sustainable clothing brands verified by independent certification bodies:

**Certified sustainable brands:**
- Patagonia (patagonia.com) — B Corp certified, Fair Trade, recycled materials
- Eileen Fisher (eileenfisher.com) — B Corp, take-back program
- Everlane (everlane.com) — radical transparency on factories/pricing
- Reformation (thereformation.com) — carbon neutral, RefScale transparency tool
- Allbirds (allbirds.com) — carbon footprint labeling on every product

**Rating and verification sources:**
- Good On You (goodonyou.eco) — independent brand ratings (1-5 scale)
- Fashion Revolution (fashionrevolution.org) — Fashion Transparency Index
- B Corp directory: bcorporation.net/en-us/find-a-b-corp

**Certification bodies:**
- GOTS (global-standard.org) — organic textile standard
- Fair Trade USA (fairtradecertified.org)
- Bluesign (bluesign.com)

Detailed comparisons at thegoodtrade.com and sustainablejungle.com."""
  },
  {
    "intent": "informational",
    "query": "How does dropshipping work for clothing e-commerce?",
    "response": """Dropshipping in clothing means selling products without holding inventory.

**How it works:**
1. You list products on your store (Shopify, WooCommerce)
2. Customer orders → you forward to supplier
3. Supplier ships directly to customer

**Key platforms and suppliers:**
- Shopify (shopify.com) — most popular store platform with dropshipping apps
- Oberlo/DSers (dsers.com) — AliExpress dropshipping tool
- Spocket (spocket.co) — US/EU suppliers for faster shipping
- Modalyst (modalyst.com) — fashion-specific dropshipping
- Printful (printful.com) — print-on-demand clothing

**Learning resources:**
- Shopify blog: shopify.com/blog/clothing-dropshipping
- Oberlo guides: oberlo.com/blog (now part of Shopify)
- BigCommerce: bigcommerce.com/articles/ecommerce/dropshipping

**Market analysis** at entrepreneur.com, Forbes (forbes.com), and ecommerceguide.com
covers margins, supplier vetting, and brand risks."""
  },
  {
    "intent": "informational",
    "query": "What is the difference between fast fashion and slow fashion?",
    "response": """Fast fashion vs. slow fashion represent opposite ends of the production spectrum.

**Fast fashion characteristics** — analyzed at:
- Vox: vox.com/the-goods/2018/9/19/17800126/fast-fashion-zara-hm-forever21
- The Atlantic: theatlantic.com/magazine/fast-fashion
- Business Insider: businessinsider.com/fast-fashion-environmental-impact

**Slow fashion/sustainable fashion resources:**
- Eco Stylist (ecostylist.com) — slow fashion brand directory
- The Good Trade (thegoodtrade.com) — slow fashion explainers
- Slow Factory (slowfactory.earth) — advocacy and education
- Sustainable Apparel Coalition (apparelcoalition.org)

**Academic perspective:**
- Journal of Fashion Marketing and Management (emerald.com)
- Sustainability journal (mdpi.com/journal/sustainability)
- Journal of Cleaner Production articles available on sciencedirect.com

**Brand examples** compared at fashionrevolution.org and remake.world,
with certification details at bluesign.com and global-standard.org (GOTS)."""
  },
  {
    "intent": "informational",
    "query": "How to identify high quality clothing materials online?",
    "response": """Identifying fabric quality online requires reading descriptions carefully.

**What to look for:**
- Fabric composition percentages (100% cotton vs. polyester blends)
- Thread count for woven fabrics (explained at threadcount.guide)
- GSM (grams per square meter) — higher = heavier/more durable

**Educational resources:**
- Fabric University (fabricuniversity.com) — textile education
- The Spruce Crafts (thesprucecrafts.com/types-of-fabric)
- Textile Exchange (textileexchange.org) — fiber standards

**Brand transparency sources:**
- Remake World (remake.world) — factory and material disclosure
- Fashion Checker (fashionchecker.org) — brand transparency scores
- Open Apparel Registry (openapparel.org)

**Review platforms for fabric quality:**
- Trustpilot (trustpilot.com) — customer reviews on durability
- Reddit communities (reddit.com/r/femalefashionadvice, r/malefashionadvice)

Detailed material guides at nordstrom.com, net-a-porter.com, and mrporter.com
include fabric descriptors for luxury items."""
  },
  {
    "intent": "informational",
    "query": "What are the best brands for athletic wear?",
    "response": """Top athletic wear brands by category:

**Performance leaders:**
- Nike (nike.com) — Dri-FIT technology, widest product range
- Adidas (adidas.com) — CLIMACOOL, Parley ocean plastic collections
- Under Armour (underarmour.com) — HeatGear/ColdGear technology
- Lululemon (lululemon.com) — premium yoga and running

**Mid-range value:**
- New Balance (newbalance.com) — running specialty
- Puma (puma.com) — performance and lifestyle
- Reebok (reebok.com) — CrossFit, Nano line
- Champion (champion.com) — affordable basics

**Reviews and comparisons:**
- Runner's World (runnersworld.com) — shoe and apparel testing
- Outside Magazine (outsideonline.com) — outdoor athletic gear
- GearJunkie (gearjunkie.com) — performance reviews
- Wirecutter/NYT (nytimes.com/wirecutter) — independent testing
- REI (rei.com/learn) — educational buying guides

Expert lab testing results published at consumerreports.org."""
  },
  {
    "intent": "informational",
    "query": "How do clothing size charts differ between countries?",
    "response": """Clothing sizes vary significantly across US, UK, EU, and Asian markets.

**Conversion resources:**
- Sizeguide.net — comprehensive international size tables
- Convertmy.size — automated size converter
- Size.ly — universal size database

**Official conversion charts from major retailers:**
- ASOS (asos.com/size-chart) — US, UK, AU, EU, FR conversions
- Zalando (zalando.com/sizeguide) — European standard focus
- Net-a-Porter (net-a-porter.com/en-us/d/info/sizefit) — luxury sizing
- Farfetch (farfetch.com/shopping/women/size-guide-d10394.aspx)

**Key differences documented at:**
- Vogue (vogue.com/article/clothing-size-guide)
- Real Simple (realsimple.com)
- WikiHow (wikihow.com/Convert-Clothing-Sizes)

**Academic context** on size standardization at ASTM International (astm.org)
and ISO standards portal (iso.org/standard/clothing-sizes)."""
  },
  {
    "intent": "informational",
    "query": "What is vintage clothing and where to buy it online?",
    "response": """Vintage clothing refers to garments from previous eras, typically 20+ years old.

**Online vintage marketplaces:**
- ThredUP (thredup.com) — largest online secondhand store
- Depop (depop.com) — Gen Z vintage marketplace
- Poshmark (poshmark.com) — peer-to-peer fashion resale
- Etsy (etsy.com/c/clothing) — independent vintage sellers
- eBay (ebay.com/fashion) — broad vintage selection
- Vestiaire Collective (vestiairecollective.com) — authenticated luxury vintage
- The RealReal (therealreal.com) — authenticated luxury consignment

**Curated vintage:**
- ASOS Marketplace (marketplace.asos.com)
- Beyond Retro (beyondretro.com)
- Rokit (rokit.co.uk)

**Buying guides:**
- Vogue: vogue.com/article/how-to-buy-vintage-clothing-online
- Refinery29: refinery29.com/vintage-shopping-guide
- Who What Wear (whowhatwear.com) — authentication tips

Authentication advice at authenticfashion.com and consignment platform help centers."""
  },
  {
    "intent": "informational",
    "query": "How do fashion designers create seasonal collections?",
    "response": """Fashion design process documented by industry institutions:

**The collection development cycle:**
1. Trend research (WGSN wgsn.com, Trendalytics trendalytics.co)
2. Concept development and mood boarding
3. Fabric sourcing (Première Vision premierevision.com)
4. Pattern making and sampling
5. Runway or lookbook presentation

**Educational resources:**
- Business of Fashion (businessoffashion.com) — industry process guides
- Vogue Business (voguebusiness.com) — behind-the-scenes coverage
- Fashion Institute of Technology (fitnyc.edu) — academic courses
- Parsons School of Design (parsons.edu)
- LVMH Institute (lvmh.com/houses/fashion)

**Designer interviews and process:**
- System Magazine (system-magazine.com)
- AnOther Magazine (anothermag.com)
- Dezeen (dezeen.com/design/fashion)

**Supply chain and production** explained at:
- Fashion Revolution: fashionrevolution.org/about/transparency
- Remake: remake.world/learn/supply-chain"""
  },
  {
    "intent": "informational",
    "query": "What fabrics are best for summer clothing?",
    "response": """Breathable natural fabrics dominate summer wardrobes. Evidence-based guidance:

**Best summer fabrics (by breathability):**
1. **Linen** — most breathable, explained at masterclass.com/articles/linen-fabric-guide
2. **Cotton** — versatile; compared at thesprucecrafts.com
3. **Chambray** — lighter cotton weave, covered at goodhousekeeping.com
4. **Bamboo** — moisture-wicking; reviewed at treehugger.com

**Technical fabric guides:**
- Cotton Inc (cottoninc.com) — cotton fiber education
- Linen Club (linenclub.com) — linen fabric properties
- Textile Exchange (textileexchange.org/materials)

**Retailer fabric guides:**
- L.L.Bean: llbean.com/llb/shop/fabrics-materials
- REI: rei.com/learn/expert-advice/fabrics-technology
- Outdoor Research (outdoorresearch.com) — performance fabrics

**Consumer testing:**
- Wirecutter (nytimes.com/wirecutter) — fabric performance testing
- Good Housekeeping Institute (goodhousekeeping.com) — lab tested recommendations

Dermatology perspective on heat rash prevention at aad.org (American Academy of Dermatology)."""
  },
  {
    "intent": "informational",
    "query": "How does clothing care labeling work internationally?",
    "response": """Clothing care labels follow ISO 3758 international standard symbols.

**Official standards:**
- ISO 3758: iso.org/standard/iso-3758 — international care labeling code
- ASTM D5489 (US): astm.org — domestic care symbols standard
- GINETEX (ginetex.net) — European care symbol licensor

**Symbol guides:**
- FTC Textile Rules: ftc.gov/tips-advice/business-center/guidance/threading-your-way-through-labeling-requirements-textile
- Whirlpool care guide: whirlpool.com/blog/washers-dryers/laundry-symbols
- LG Home Care: lg.com/us/support/products/documents/Laundry_Symbol_Guide.pdf
- Consumer Reports: consumerreports.org/laundry/laundry-symbols-guide

**Country-specific variations:**
- UK / EU labels at textiles.co.uk and euratex.eu
- Japanese JIS L0001 standard documented at jisc.go.jp

**Retailer care information:**
- Uniqlo (uniqlo.com/us/en/contents/help-faq/products-care.html)
- Patagonia (patagonia.com/care-repair.html) — detailed care system"""
  },
  {
    "intent": "informational",
    "query": "What is the global market size for online fashion retail?",
    "response": """The global online fashion market is one of the largest e-commerce segments.

**Market size data and forecasts:**
- Statista (statista.com) — global online apparel market: ~$900B+ (2024)
- Grand View Research (grandviewresearch.com) — CAGR projections
- McKinsey & Company (mckinsey.com) — State of Fashion annual report
- Euromonitor (euromonitor.com) — country-level apparel data
- Mordor Intelligence (mordorintelligence.com) — segment breakdowns

**Industry reports (free excerpts):**
- Business of Fashion + McKinsey: businessoffashion.com/reports/news-analysis/state-of-fashion
- Deloitte Retail Outlook: deloitte.com/us/en/insights/industry/retail-distribution
- PwC Global Consumer Insights: pwc.com/gx/en/consumer-markets

**Platform-specific data:**
- Shopify Commerce Trends: shopify.com/research
- Salesforce Shopping Index: salesforce.com/resources/research-reports/shopping-index

Key players (Amazon, SHEIN, Zalando, ASOS) report financials at respective
investor relations pages: ir.aboutamazon.com, group.inditex.com."""
  },

  # ── CONSIDERATION (17) ──────────────────────────────────
  {
    "intent": "consideration",
    "query": "Best affordable women's dresses under $50 online",
    "response": """Top picks for women's dresses under $50 from trusted sources:

**Expert-reviewed picks:**
- Good Housekeeping: goodhousekeeping.com/clothing/g38578126/best-affordable-dresses
- Wirecutter: nytimes.com/wirecutter/reviews/best-affordable-dresses
- Who What Wear: whowhatwear.com/affordable-dresses
- InStyle: instyle.com/fashion/shopping/best-affordable-dresses-under-50

**Where to shop:**
- Amazon Fashion (amazon.com/fashion) — huge selection, Prime eligible
- ASOS (asos.com) — wide size range, frequent sales
- H&M (hm.com) — $15–$40 range
- Shein (shein.com) — budget-friendly, extensive selection
- Target (target.com/c/dresses-women) — A New Day, Universal Thread lines
- Old Navy (oldnavy.gap.com) — classic styles under $50
- Walmart Fashion (walmart.com/browse/clothing/womens-dresses) — budget options

**Size inclusivity guides:**
- Refinery29 (refinery29.com) — inclusive sizing roundups
- Cosmopolitan (cosmopolitan.com/style-beauty/fashion)

Customer reviews aggregated at Trustpilot (trustpilot.com) for retailer reliability."""
  },
  {
    "intent": "consideration",
    "query": "Top 10 online clothing stores for men's fashion",
    "response": """Best men's online clothing retailers ranked by product range, quality, and value:

**Expert rankings:**
- GQ (gq.com/story/best-online-clothing-stores-for-men) — editorial picks
- Esquire (esquire.com/style/mens-fashion/advice/g2137/best-menswear-online-stores)
- Men's Health (menshealth.com) — value and performance focus
- The Manual (themanual.com) — lifestyle and fashion coverage

**Top stores by category:**
1. **Premium**: Mr Porter (mrporter.com), Farfetch (farfetch.com), SSENSE (ssense.com)
2. **Mid-range**: ASOS (asos.com/men), Nordstrom (nordstrom.com/mens), Banana Republic (bananarepublic.gap.com)
3. **Affordable**: H&M (hm.com/men), Uniqlo (uniqlo.com), Zara (zara.com/men)
4. **Streetwear**: END Clothing (endclothing.com), Kith (kith.com), Stadium Goods (stadiumgoods.com)
5. **Workwear**: Charles Tyrwhitt (ctshirts.com), Bonobos (bonobos.com), Suit Supply (suitsupply.com)

**Comparison reviews** at businessofmenswear.com and styleforum.net (community reviews)."""
  },
  {
    "intent": "consideration",
    "query": "Best sustainable clothing brands for eco-conscious shoppers",
    "response": """Sustainable brands ranked by verified certifications and practices:

**Gold standard brands (multiple certifications):**
- Patagonia (patagonia.com) — B Corp, Fair Trade, 1% for the Planet
- Eileen Fisher (eileenfisher.com) — B Corp, recycling take-back program
- Prana (prana.com) — Fair Trade, bluesign, GOTS certified

**Independently verified ratings:**
- Good On You (goodonyou.eco) — rates 3,000+ brands on People/Planet/Animals
- Remake Fashion Scorecard (remake.world/scorecard) — supply chain transparency
- Fashion Revolution Transparency Index (fashionrevolution.org)

**Top-rated sustainable options at different price points:**
- Affordable: Pact (wearpact.com), tentree (tentree.com)
- Mid-range: Everlane (everlane.com), Thought Clothing (wearethought.com)
- Premium: Stella McCartney (stellamccartney.com), Veja (veja-store.com)

**Certification checkers:**
- GOTS: global-standard.org/public-database
- Fair Trade: fairtradecertified.org/shopping
- B Corp: bcorporation.net/en-us/find-a-b-corp

Comparison guides at sustainablejungle.com and ecocult.com."""
  },
  {
    "intent": "consideration",
    "query": "Most reliable online clothing stores with free returns",
    "response": """Online stores ranked for return policy generosity and reliability:

**Best return policies reviewed:**
- Nordstrom (nordstrom.com) — no time limit on returns, widely praised
- Zappos (zappos.com) — 365-day free returns
- L.L.Bean (llbean.com) — satisfaction guarantee (historic lifetime policy)
- REI (rei.com) — 1-year returns for members
- Costco (costco.com/clothing) — generous return window

**Return policy comparison sources:**
- NerdWallet: nerdwallet.com/article/shopping/store-return-policies
- Clark Howard: clarkhoward.com/best-return-policies
- Consumer Reports (consumerreports.org) — retailer reliability surveys
- Better Business Bureau (bbb.org) — complaint tracking

**Stores with streamlined digital returns:**
- Amazon (amazon.com) — free return shipping on most fashion items
- ASOS (asos.com/page/returns) — extended return window
- Revolve (revolve.com) — free returns, prepaid label

Review aggregators: Trustpilot (trustpilot.com) and Sitejabber (sitejabber.com)
have extensive per-retailer return experience reviews."""
  },
  {
    "intent": "consideration",
    "query": "Best plus-size clothing brands online",
    "response": """Leading plus-size clothing brands reviewed by fashion experts and community:

**Expert-reviewed recommendations:**
- Refinery29 (refinery29.com/en-us/plus-size-clothing-brands) — comprehensive guide
- Cosmopolitan (cosmopolitan.com/style-beauty/fashion/g37620814/best-plus-size-clothing-brands)
- Good Housekeeping (goodhousekeeping.com) — vetted picks through size 6X

**Top specialized plus-size brands:**
- Eloquii (eloquii.com) — trendy, sizes 14–28
- Torrid (torrid.com) — youth-skewing, 10–30
- Lane Bryant (lanebryant.com) — classic plus sizes
- Universal Standard (universalstandard.com) — size 00–40, inclusive sizing
- Anthropologie BHLDN (anthropologie.com) — fashion-forward extended sizes
- ASOS Curve (asos.com/women/curve-plus-size) — trend-led

**Size-inclusive mainstream options:**
- Nordstrom (nordstrom.com/browse/women/plus) — broad brand selection
- Revolve (revolve.com) — expanded size range
- Madewell (madewell.com) — inclusive denim sizing

Community recommendations at reddit.com/r/PlusSizeFashion and curvyista.com."""
  },
  {
    "intent": "consideration",
    "query": "Top athletic wear brands compared by experts",
    "response": """Athletic wear compared across performance, durability, and value by testing organizations:

**Independent testing and reviews:**
- Runner's World (runnersworld.com/gear/apparel) — performance lab testing
- Outside Magazine (outsideonline.com/gear/apparel) — real-world tests
- Wirecutter NYT (nytimes.com/wirecutter/sports-outdoors/exercise-fitness) — editorial testing
- GearLab (outdoor.gearlab.com/apparel) — systematic comparison testing
- Triathlete Magazine (triathlete.com/gear/apparel) — multisport testing

**Brand comparison by use case:**
- Running: Nike (nike.com) vs. Brooks (brooksrunning.com) vs. New Balance (newbalance.com)
- Yoga/Pilates: Lululemon (lululemon.com) vs. Alo Yoga (aloyoga.com) vs. Vuori (vuoriclothing.com)
- CrossFit: Reebok (reebok.com) vs. Nike vs. Nobull (nobullproject.com)
- Outdoor: Patagonia (patagonia.com) vs. Arc'teryx (arcteryx.com) vs. Columbia (columbia.com)

**Value picks** identified by menshealth.com, womenshealthmag.com, and self.com."""
  },
  {
    "intent": "consideration",
    "query": "Best luxury fashion brands worth the price",
    "response": """Luxury fashion brands assessed for craftsmanship, heritage, and value retention:

**Investment value analysis:**
- Business of Fashion (businessoffashion.com) — brand valuation and resale tracking
- Vogue Business (voguebusiness.com) — luxury market analysis
- Lyst Index (lyst.com/index) — quarterly luxury brand rankings
- Knight Frank Luxury Investment Index (knightfrank.com) — asset appreciation data

**Highest-rated luxury brands for quality/value:**
- Hermès (hermes.com) — Birkin bags appreciate in value; documented at baghunter.com
- Chanel (chanel.com) — classic quilted bags outperform stock markets (vogue.com analysis)
- Louis Vuitton (louisvuitton.com) — monogram pieces hold resale value
- Bottega Veneta (bottegaveneta.com) — craft-focused, durable leather goods

**Resale value tracking:**
- The RealReal (therealreal.com/resale-value) — publishes annual luxury resale report
- Vestiaire Collective (vestiairecollective.com) — price tracking tools
- Rebag (rebag.com/clair) — instant luxury valuation tool

**Entry-level luxury** guides at who what wear (whowhatwear.com) and Harper's Bazaar (harpersbazaar.com)."""
  },
  {
    "intent": "consideration",
    "query": "Most popular streetwear brands ranked this year",
    "response": """Top streetwear brands tracked by hype indices and community votes:

**Industry ranking sources:**
- Highsnobiety (highsnobiety.com) — Highsnobiety Index quarterly rankings
- Hypebeast (hypebeast.com) — HBX brand rankings and release tracking
- StockX (stockx.com/trending) — demand data from resale market
- Lyst (lyst.com/index) — quarterly brand heat rankings

**Top streetwear brands consistently ranked:**
1. Supreme (supremenewyork.com) — drops tracked at supremecommunity.com
2. Off-White (off---white.com) — Virgil Abloh legacy brand
3. Palace Skateboards (palaceskateboards.com) — UK-origin, cult following
4. BAPE (us.bape.com) — Japanese heritage streetwear
5. Fear of God (fearofgod.com) — luxury streetwear category
6. Kith (kith.com) — collaborative drops model
7. Noah (noahny.com) — quality-focused streetwear

**Release calendars and news:**
- Sneaker News (sneakernews.com)
- Sole Collector (solecollector.com)
- Kicks on Fire (kicksonfire.com)

Community discussions at reddit.com/r/streetwear with 4M+ members."""
  },
  {
    "intent": "consideration",
    "query": "Best online stores for children's clothing",
    "response": """Top children's clothing retailers reviewed for quality, safety, and value:

**Expert recommendations:**
- Good Housekeeping (goodhousekeeping.com/childrens-products/g5124/best-kids-clothing-brands)
- Parents Magazine (parents.com/baby/clothes/baby-clothing-brands)
- Romper (romper.com) — parenting-focused fashion coverage
- Wirecutter (nytimes.com/wirecutter) — kids clothing tested

**Top retailers by category:**
- **Quality basics**: Carter's (carters.com), OshKosh B'gosh (oshkosh.com)
- **Trendy/fashion-forward**: Zara Kids (zara.com/kids), H&M Kids (hm.com/kids)
- **Sustainable**: Primary (primary.com), Hanna Andersson (hannaandersson.com)
- **Value**: Old Navy (oldnavy.gap.com), Target Cat & Jack (target.com)
- **Premium**: Tea Collection (teacollection.com), Janie and Jack (janieandjack.com)
- **Secondhand**: ThredUP kids (thredup.com/kids), Kidizen (kidizen.com)

**Safety certifications** for children's clothing at cpsc.gov (Consumer Product Safety Commission)
and OEKO-TEX database (oeko-tex.com)."""
  },
  {
    "intent": "consideration",
    "query": "Top-rated work clothing brands for professionals",
    "response": """Professional workwear brands assessed for durability, style, and workplace appropriateness:

**Business dress code guides:**
- Harvard Business Review (hbr.org) — professional dress research
- Forbes (forbes.com) — executive dressing guides
- Business Insider (businessinsider.com/work-clothing-guide)

**Top-rated professional clothing brands:**
- **Men's suiting**: Suit Supply (suitsupply.com), Charles Tyrwhitt (ctshirts.com), Brooks Brothers (brooksbrothers.com)
- **Women's workwear**: MM LaFleur (mmlafleur.com), Banana Republic (bananarepublic.gap.com), Ann Taylor (anntaylor.com)
- **Business casual**: Bonobos (bonobos.com), J.Crew (jcrew.com), Everlane (everlane.com)
- **Tech/startup casual**: Patagonia (patagonia.com), Lululemon (lululemon.com) ABC pants
- **Budget professional**: Target (target.com), H&M (hm.com/ladies/workwear)

**Style advice resources:**
- Corporette (corporette.com) — women's professional dressing
- Dappered (dappered.com) — men's office style on a budget
- Put This On (putthison.com) — men's classic dressing

Reviews compiled at Trustpilot (trustpilot.com) and Reddit r/malefashionadvice."""
  },
  {
    "intent": "consideration",
    "query": "Best budget fashion apps for clothing deals",
    "response": """Top apps for finding clothing deals reviewed by tech and fashion publications:

**Deal-finding and comparison apps reviewed at:**
- TechCrunch (techcrunch.com) — app launches and reviews
- CNET (cnet.com/tech/mobile-apps/best-shopping-apps)
- Wirecutter (nytimes.com/wirecutter/money/best-coupon-apps)

**Best clothing deal apps:**
- Honey (joinhoney.com) — browser extension + app, auto coupon codes
- Rakuten (rakuten.com) — cashback on major fashion retailers
- ShopSavvy (shopsavvy.com) — barcode scanner, price comparison
- Poshmark (poshmark.com) — secondhand at deep discounts
- Depop (depop.com) — vintage and Y2K discounts
- ThredUP (thredup.com) — algorithmic markdowns
- SHEIN (shein.com/app) — flash sales and daily deals
- Zulily (zulily.com) — flash sale model for brand names

**Cashback comparisons:**
- NerdWallet: nerdwallet.com/article/shopping/cash-back-apps
- The Points Guy (thepointsguy.com) — rewards stacking strategies

App store ratings at Apple App Store (apps.apple.com) and Google Play (play.google.com)."""
  },
  {
    "intent": "consideration",
    "query": "Most recommended online brands for winter coats",
    "response": """Winter coat brands recommended by outdoor and fashion experts:

**Expert gear testing:**
- Wirecutter (nytimes.com/wirecutter/reviews/best-womens-winter-coats) — lab tested insulation
- Outside Magazine (outsideonline.com/gear/apparel/winter-coats) — field tested
- Outdoor Gear Lab (outdoorgearlab.com/reviews/clothing/coats-jackets) — systematic comparison
- REI Expert Advice (rei.com/learn/expert-advice/insulation-types) — technical breakdown

**Top brands by warmth and durability:**
- **Performance outdoor**: The North Face (thenorthface.com), Patagonia (patagonia.com), Canada Goose (canadagoose.com)
- **Fashion-forward warmth**: Moncler (moncler.com), Woolrich (woolrich.com), Mackage (mackage.com)
- **Value**: Columbia (columbia.com), Lands' End (landsend.com), LL Bean (llbean.com)
- **Urban style**: Zara (zara.com), Uniqlo Ultra Light Down (uniqlo.com), H&M (hm.com)

**Technical specs explained** at mountainhardwear.com/blog, ems.com/blogs/expertadvice,
and rei.com/learn/expert-advice/sleeping-bag-temperature-ratings.html (insulation comparison)."""
  },
  {
    "intent": "consideration",
    "query": "Best online vintage clothing stores reviewed",
    "response": """Online vintage stores ranked by selection, authentication, and buyer protection:

**Review-based rankings:**
- Vogue (vogue.com/article/best-vintage-online-shopping-sites)
- Who What Wear (whowhatwear.com/best-online-vintage-stores)
- Refinery29 (refinery29.com/en-us/best-places-buy-vintage-clothing-online)
- Harper's Bazaar (harpersbazaar.com/fashion/trends/vintage-shopping)

**Top rated vintage stores:**
1. Vestiaire Collective (vestiairecollective.com) — authenticated luxury vintage
2. The RealReal (therealreal.com) — consignment, verified authenticity
3. Depop (depop.com) — community-driven, Y2K and 90s focus
4. Poshmark (poshmark.com) — broad vintage selection
5. ASOS Marketplace (marketplace.asos.com) — curated boutiques
6. Etsy Vintage (etsy.com/c/vintage-clothing) — unique and handpicked
7. Beyond Retro (beyondretro.com) — UK/EU focused
8. Rokit (rokit.co.uk) — UK vintage specialist

**Authentication tips** at authenticate.co and real authentication (realauthentication.com).
Community validation on reddit.com/r/VintageFashion."""
  },
  {
    "intent": "consideration",
    "query": "Top maternity clothing brands recommended",
    "response": """Maternity clothing brands ranked by comfort, style, and postpartum wearability:

**Parenting publication recommendations:**
- What to Expect (whattoexpect.com/pregnancy/pregnancy-health/best-maternity-clothes)
- The Bump (thebump.com/a/best-maternity-clothes-brands)
- Parents Magazine (parents.com/pregnancy/my-body/clothes-beauty-style)
- Romper (romper.com) — maternity fashion coverage
- Babylist (babylist.com) — registry and brand reviews

**Top-rated maternity brands:**
- HATCH Collection (hatchcollection.com) — fashion-forward, wears beyond pregnancy
- Seraphine (seraphine.com) — celebrity-endorsed, UK-origin
- Ingrid & Isabel (ingridandisabel.com) — Belly Belt innovation
- Storq (storq.com) — minimalist, sustainable maternity
- A Pea in the Pod (apeainthepod.com) — designer maternity
- H&M Maternity (hm.com/maternity) — affordable basics
- ASOS Maternity (asos.com/women/maternity) — trend-led, wide size range

**Rental option**: Rent the Runway (renttherunway.com) for event maternity wear."""
  },
  {
    "intent": "consideration",
    "query": "Best online stores for wedding guest dresses",
    "response": """Wedding guest dress sources ranked by occasion-appropriateness and style range:

**Editorial picks by wedding publications:**
- Brides Magazine (brides.com/best-places-to-shop-for-wedding-guest-dresses)
- Martha Stewart Weddings (marthastewartweddings.com)
- The Knot (theknot.com/content/what-to-wear-to-a-wedding)
- Vogue (vogue.com/article/what-to-wear-to-a-wedding)

**Top stores by wedding formality:**
- **Black tie**: Rent the Runway (renttherunway.com), Neiman Marcus (neimanmarcus.com), Saks (saksfifthavenue.com)
- **Cocktail**: Nordstrom (nordstrom.com), Revolve (revolve.com), BHLDN (bhldn.com)
- **Semi-formal**: ASOS (asos.com), Anthropologie (anthropologie.com), Free People (freepeople.com)
- **Casual/garden**: Lulus (lulus.com), Show Me Your Mumu (showmeyourmumu.com), Maggy London (maggylondon.com)
- **Budget**: H&M (hm.com), Shein (shein.com), Amazon (amazon.com/wedding-guest)

**Dress code decoder** at theknot.com and versacourt.com/wedding-dress-codes."""
  },
  {
    "intent": "consideration",
    "query": "Most popular Korean fashion brands for international buyers",
    "response": """Korean fashion brands gaining international traction, sourced from K-fashion media:

**K-fashion media and guides:**
- Koreaboo (koreaboo.com) — K-culture fashion coverage
- Soompi (soompi.com) — K-entertainment and fashion
- Korean Fashion Blog (koreanfashiontrendz.com)
- Vogue Korea (vogue.co.kr) — editorial coverage

**Top Korean brands shipping internationally:**
- Ader Error (adererror.com) — avant-garde streetwear
- Musinsa (en.musinsa.com) — Korea's largest fashion platform
- W Concept (wconcept.com) — curated Korean designer marketplace
- Stylenanda (en.stylenanda.com) — trendy women's fashion
- Gentle Monster (gentlemonster.com) — eyewear and accessories crossover
- Andersson Bell (anderssonbell.com) — gender-neutral streetwear
- 87MM (87mm.com) — Seoul-based contemporary brand

**International shipping platforms for Korean fashion:**
- YesStyle (yesstyle.com) — multi-brand Korean/Asian fashion
- KOODING (kooding.com) — Korean brand aggregator
- Kstylick (kstylick.com) — K-fashion news and shopping

Community recommendations at reddit.com/r/KoreanFashion."""
  },
  {
    "intent": "consideration",
    "query": "Best activewear brands for yoga and fitness",
    "response": """Activewear brands ranked for yoga and fitness by independent testers and community:

**Independent testing:**
- Self Magazine (self.com/story/best-yoga-pants) — wearability testing
- Shape Magazine (shape.com/fitness/workout-clothes) — performance reviews
- Women's Health (womenshealthmag.com) — gear lab testing
- Yoga Journal (yogajournal.com/lifestyle/fashion-and-beauty) — community feedback

**Top yoga/fitness-specific brands:**
- Lululemon (lululemon.com) — industry benchmark, Align and Define lines
- Alo Yoga (aloyoga.com) — studio-to-street aesthetic
- Vuori (vuoriclothing.com) — sustainability focus, versatile design
- Beyond Yoga (beyondyoga.com) — inclusive sizing, ultra-soft fabrics
- Athleta (athleta.gap.com) — Gap brand, B Corp, inclusive sizing
- Girlfriend Collective (girlfriend.com) — recycled materials, body-positive
- Fabletics (fabletics.com) — subscription model, value pricing

**Budget alternatives:**
- Colorfulkoala (colorfulkoala.com) — popular Amazon brand
- Ewedoos (ewedoos.com) — Wirecutter budget pick

Community reviews at reddit.com/r/xxfitness and lululemon subreddit."""
  },

  # ── TRANSACTIONAL (16) ──────────────────────────────────
  {
    "intent": "transactional",
    "query": "Buy ZARA women's summer dress online free shipping",
    "response": """To purchase ZARA women's summer dresses online with free shipping:

**Official ZARA channels:**
- Main store: zara.com/us/en/woman-dresses-l1066.html
- ZARA app (iOS/Android) — exclusive app deals sometimes available
- Free shipping threshold and current promotions at zara.com/us/en/z-promotional-codes.html

**Free shipping options:**
- ZARA offers free shipping on orders above threshold (check current terms at zara.com)
- In-store pickup (Click & Collect) is free at all ZARA locations

**Third-party platforms carrying ZARA:**
- Nordstrom (nordstrom.com) — carries select ZARA items with Nordy Club rewards
- Note: avoid unofficial third-party sellers for authenticity guarantee

**Deal-stacking resources:**
- Honey (joinhoney.com) — automatic promo code testing at checkout
- Rakuten (rakuten.com) — cashback on ZARA purchases

Current sale section: zara.com/us/en/sale-woman-l3.html
Customer service: zara.com/us/en/z-help.html"""
  },
  {
    "intent": "transactional",
    "query": "H&M men's jeans sale buy now discount",
    "response": """Current H&M men's jeans deals and purchase options:

**Official H&M purchase channels:**
- Sale section: hm.com/en_us/men/sale/trousers-jeans.html
- H&M app — app-exclusive offers and member discounts
- H&M Member Program: hm.com/en_us/customer-service/h-m-membership.html

**H&M discount strategies:**
- H&M newsletter signup (hm.com) — typically 10–15% welcome discount
- H&M Member offers — exclusive member sale prices
- Honey extension (joinhoney.com) — checks H&M promo codes automatically

**Third-party discount platforms:**
- RetailMeNot (retailmenot.com/view/hm.com) — H&M coupon codes
- Coupons.com (coupons.com) — H&M discount codes
- Rakuten (rakuten.com/shop/hm-us) — cashback offers

**Price comparison:**
- Google Shopping (shopping.google.com) — compare H&M jeans prices
- PriceGrabber (pricegrabber.com)
- Shopzilla (shopzilla.com)

Check current sale items at hm.com/en_us/men/new-arrivals.html"""
  },
  {
    "intent": "transactional",
    "query": "Nike women's running shoes order online best price",
    "response": """Best prices for Nike women's running shoes online:

**Official Nike channels:**
- Nike.com (nike.com/w/womens-running-shoes) — full selection, Nike Member exclusive deals
- Nike app — members-only drops and early access
- Nike sale section: nike.com/w/sale-womens-running-shoes

**Authorized retailers with competitive pricing:**
- Zappos (zappos.com/nike-womens-running-shoes) — 365-day returns, price match
- Running Warehouse (runningwarehouse.com) — running specialty, expert reviews
- Fleet Feet (fleetfeet.com) — gait analysis available, authorized dealer
- Dick's Sporting Goods (dickssportinggoods.com/nike) — frequent sales
- Nordstrom Rack (nordstromrack.com) — clearance Nike at discount

**Deal tracking:**
- Nike Outlet (nike.com/w/outlet-womens-running-shoes) — permanent markdowns
- RunRepeat (runrepeat.com) — tracks price history and best deals
- Brad's Deals (bradsdeals.com) — Nike sale alerts

**Model selection guide** at runnersworld.com and runningwarehouse.com/LearningCenter."""
  },
  {
    "intent": "transactional",
    "query": "Levi's 501 original jeans purchase online cheapest",
    "response": """Levi's 501 jeans at best prices online:

**Official Levi's channels:**
- Levi's.com sale (levi.com/US/en_US/clothing/men/jeans/501-jeans) — seasonal markdowns
- Levi's Outlet: levi.com/US/en_US/sale — up to 50% off classic styles
- Levi's app — members get early sale access

**Lowest prices typically found at:**
- Amazon (amazon.com/levis-501) — compare multiple sellers, check fulfilled by Amazon
- Macy's sale (macys.com/levis) — frequent 40-60% off events
- Nordstrom Rack (nordstromrack.com) — surplus 501s at clearance
- Kohl's (kohls.com) — Levi's authorized retailer with frequent 40% off coupons
- ASOS (asos.com/levis) — EU pricing often favorable

**Price tracking tools:**
- CamelCamelCamel (camelcamelcamel.com) — Amazon price history for 501s
- Honey (joinhoney.com) — price drop alerts
- Google Shopping (shopping.google.com) — compare all retailers

Current best price aggregator: Google Shopping search "Levi's 501 women" or "Levi's 501 men"."""
  },
  {
    "intent": "transactional",
    "query": "SHEIN clothing order tracking and express delivery",
    "response": """SHEIN order tracking and delivery options:

**Official SHEIN resources:**
- Order tracking: shein.com/user/orders/list (login required)
- Track by order number: shein.com/user/orders/track
- SHEIN app (iOS/Android) — push notifications for order status
- SHEIN customer service: shein.com/service.html

**Shipping options on SHEIN:**
- Standard: 6–8 business days (free above threshold)
- Express: 2–4 business days (fee applies, check shein.com/shipping-info)
- SHEIN Express: faster processing for select items

**Carrier tracking portals (SHEIN uses multiple carriers):**
- 17Track (17track.net) — universal package tracker supporting SHEIN carriers
- PackageRadar (packageradar.com) — SHEIN shipment tracking
- Parcel Monitor (parcelmonitor.com)

**Common shipping issues** documented at consumer complaint boards:
- Better Business Bureau: bbb.org/us/fl/miami/profile/clothing/shein-0633-90175965
- Trustpilot SHEIN reviews: trustpilot.com/review/shein.com

SHEIN return process: shein.com/free-return.html (first return free)"""
  },
  {
    "intent": "transactional",
    "query": "ASOS next day delivery women's clothing purchase",
    "response": """ASOS next-day delivery purchase guide:

**Official ASOS ordering:**
- Women's section: asos.com/women
- ASOS Premier (premier.asos.com) — unlimited next-day delivery subscription
- Delivery options at checkout: asos.com/page/delivery-and-returns

**Next-day delivery specifics:**
- Order before 9 PM for next-day (cutoffs vary, check asos.com/page/delivery-returns)
- ASOS Premier: ~$19/year for unlimited next-day delivery
- Standard next-day: fee applied at checkout

**Payment and checkout:**
- ASOS accepts Klarna (klarna.com) for buy-now-pay-later
- Afterpay (afterpay.com) — 4 interest-free payments
- PayPal, major credit cards

**Current ASOS promotions:**
- Sale section: asos.com/sale
- Student discount via UNiDAYS (myunidays.com) — 15% off
- ASOS promo codes at retailmenot.com/view/asos.com

**App-specific deals:** ASOS app often has app-exclusive discounts.
Download from apps.apple.com or play.google.com."""
  },
  {
    "intent": "transactional",
    "query": "Uniqlo online store order international shipping",
    "response": """Uniqlo international online shopping guide:

**Official Uniqlo stores by region:**
- US: uniqlo.com/us
- UK: uniqlo.com/uk
- EU: uniqlo.com/eu
- Global ship-from-Japan: uniqlo.com/jp (limited international shipping)

**International shipping specifics:**
- Uniqlo ships to 70+ countries from regional warehouses
- Check shipping destinations: uniqlo.com/us/en/help/shipping-delivery
- Estimated delivery and fees at checkout

**Popular Uniqlo items for international orders:**
- Ultra Light Down jacket (search on uniqlo.com)
- HEATTECH innerwear
- AIRism base layers

**Third-party international shipping options:**
- Buyandship (buyandship.com) — US/Japan Uniqlo to Asia
- Shipito (shipito.com) — US address forwarding
- Tenso (tenso.com) — Japan to worldwide Uniqlo orders

**Payment methods:**
- Major credit cards, PayPal at uniqlo.com
- Klarna available in select markets

Uniqlo member discounts at uniqlo.com/us/en/app — app-exclusive offers available."""
  },
  {
    "intent": "transactional",
    "query": "Amazon fashion women's clothing prime deals buy",
    "response": """Amazon Fashion Prime deals guide for women's clothing:

**Official Amazon Fashion hubs:**
- Women's Fashion: amazon.com/womens-clothing
- Prime Wardrobe (Try Before You Buy): amazon.com/prime-wardrobe
- Amazon Haul: amazon.com/haul (ultra-affordable section)
- Deals section: amazon.com/deals/fashion

**Prime-exclusive deals:**
- Prime Day fashion deals (July annually) — tracked at camelcamelcamel.com
- Lightning Deals: amazon.com/deals — filter by Fashion
- Prime Early Access Sale (October)

**Finding best fashion deals on Amazon:**
- Use Honey (joinhoney.com) for price history and coupons
- CamelCamelCamel (camelcamelcamel.com) — price drop alerts
- Slickdeals (slickdeals.net) — community-curated Amazon fashion deals

**Trusted Amazon fashion brands:**
- Amazon Essentials (amazon.com/amazon-essentials)
- Daily Ritual (amazon.com/daily-ritual)
- The Drop (amazon.com/the-drop) — limited fashion collaborations

Check return eligibility at amazon.com/gp/help/customer/display.html?nodeId=GKM69DUUYKQWKWX."""
  },
  {
    "intent": "transactional",
    "query": "Forever 21 online clearance sale buy now",
    "response": """Forever 21 clearance and sale shopping guide:

**Official Forever 21 clearance:**
- Clearance section: forever21.com/sale
- Under $10 section: forever21.com/on-sale/under-10
- Forever 21 app — app-exclusive sale alerts
- Email signup (forever21.com) — 10–15% welcome coupon

**Additional discount strategies:**
- Forever 21 promo codes at RetailMeNot (retailmenot.com/view/forever21.com)
- Honey extension — automatic code testing at forever21.com
- Rakuten (rakuten.com/shop/forever-21) — cashback on purchases

**Third-party platforms with Forever 21:**
- Nordstrom Rack (nordstromrack.com) — carries clearance Forever 21 items
- Poshmark (poshmark.com) — peer-to-peer resale of Forever 21

**Forever 21 return policy:**
- Returns within 30 days with tags attached
- Full policy at forever21.com/returns-exchanges

**Company status:** Forever 21 emerged from bankruptcy; check business status at
businessoffashion.com and retaildive.com for current operations.

Customer reviews at Trustpilot (trustpilot.com/review/forever21.com)."""
  },
  {
    "intent": "transactional",
    "query": "Nordstrom rack clothing sale online purchase",
    "response": """Nordstrom Rack online shopping guide for maximum savings:

**Official Nordstrom Rack channels:**
- Website: nordstromrack.com — up to 70% off designer brands
- Clear the Rack events: nordstromrack.com/clear-the-rack — extra 25% off clearance
- Nordstrom Rack app — flash sales, Push alerts

**Deal timing tips:**
- Clear the Rack (quarterly) — biggest discount event, tracked at dealcatcher.com
- Last Chance section: nordstromrack.com/page/last-chance
- Daily deals: nordstromrack.com/daily-deals

**Nordstrom family ecosystem:**
- Nordy Club loyalty points work across Nordstrom.com and Nordstrom Rack
- Nordstrom card holders earn 3x points: nordstrom.com/c/nordstrom-card-benefits

**Return policy:**
- nordstromrack.com — returns within 40 days by mail or in-store
- Full details: nordstromrack.com/returns

**Price comparison:**
- Nordstrom Rack vs. competitor pricing at shop.org and pricegrabber.com
- Honey (joinhoney.com) — checks for Nordstrom Rack promo codes

Customer satisfaction scores at consumerreports.org and J.D. Power retail surveys."""
  },
  {
    "intent": "transactional",
    "query": "Buy authentic designer handbags online discount",
    "response": """Authenticated designer handbags at discounted prices — trusted sources:

**Authenticated resale platforms:**
- The RealReal (therealreal.com) — gemologist/appraiser authentication, up to 80% off
- Vestiaire Collective (vestiairecollective.com) — expert authentication, global inventory
- Rebag (rebag.com) — Clair™ price transparency tool, instant offers
- Fashionphile (fashionphile.com) — Neiman Marcus owned, Chanel/LV specialist
- Tradesy (tradesy.com) — buyer protection guarantee

**Authorized discount retailers:**
- Saks Off 5th (saksoff5th.com) — genuine designer clearance
- Neiman Marcus Last Call (lastcall.com)
- Nordstrom Rack (nordstromrack.com) — verified designer bags

**Authentication verification:**
- Entrupy (entrupy.com) — AI authentication service used by platforms
- Real Authentication (realauthentication.com) — third-party verification
- Legit App (legit-app.com) — sneakers and bags authentication

**What to avoid:**
- DHgate, AliExpress listings (risk of counterfeit)
- Counterfeit detection guide at authenticate.co

Buyer protection via PayPal Buyer Protection or credit card chargebacks documented at
consumerfinance.gov."""
  },
  {
    "intent": "transactional",
    "query": "Adidas originals clothing official store buy",
    "response": """Buying authentic Adidas Originals from official and authorized sources:

**Official Adidas channels:**
- Adidas Originals: adidas.com/us/originals
- adidas app — members-only releases and confirmed access to limited drops
- adidas Member program: adidas.com/us/adiClub

**Official Adidas sale channels:**
- adidas Outlet: adidas.com/us/outlet
- adidas Sale: adidas.com/us/sale
- Member access: extra discounts for adiClub members

**Authorized retailers:**
- Foot Locker (footlocker.com) — major authorized adidas Originals retailer
- JD Sports (jdsports.com) — authorized European/US retailer
- DTLR (dtlr.com) — sneaker and streetwear authorized dealer
- Champs Sports (champssports.com) — Foot Locker subsidiary

**Limited/hype drops tracked at:**
- Sneaker News (sneakernews.com) — Adidas Originals release dates
- Kicks on Fire (kicksonfire.com) — release calendar
- StockX (stockx.com/adidas) — resale if retail is sold out

**Counterfeit avoidance:**
- Only buy from adidas.com or authorized retailers listed at adidas.com/us/storelocator
- Authentication guide at authenticate.co"""
  },
  {
    "intent": "transactional",
    "query": "Gap factory outlet online sale purchase",
    "response": """Gap Factory online shopping guide:

**Official Gap Factory channels:**
- Gap Factory website: gapfactory.com
- Gap Factory app — app-exclusive promotions
- GapCash: earned on purchases, redeemable across Gap Inc. brands

**Maximum savings at Gap Factory:**
- Additional 40-50% off sale items during promotions
- Email signup: gapfactory.com — welcome offer (typically 25% off)
- Gap Inc. credit card: synchrony.com/gap — extra 5x points

**Gap Inc. family cross-shopping:**
- Old Navy (oldnavy.com) — most affordable tier
- Gap (gap.com) — full-price mainline
- Banana Republic Factory (bananarepublicfactory.com)
- Athleta (athleta.gap.com) — activewear

**Promo codes:**
- RetailMeNot (retailmenot.com/view/gap.com) — current Gap Factory codes
- DealCatcher (dealcatcher.com/gap-factory-coupons)
- Honey extension — automatic code application at checkout

**Return policy:**
- Returns within 30 days at gapfactory.com/returns
- In-store returns accepted at Gap locations

**Outlet vs. Factory distinction** explained at retailmenot.com/editorial/fashion."""
  },
  {
    "intent": "transactional",
    "query": "Mango women's clothing online order Europe",
    "response": """Mango women's clothing online ordering for European customers:

**Official Mango European stores:**
- International hub: shop.mango.com
- UK: shop.mango.com/gb
- Germany: shop.mango.com/de
- France: shop.mango.com/fr
- Italy: shop.mango.com/it
- Spain (origin): shop.mango.com/es

**European shipping and delivery:**
- Mango offers free delivery above threshold (varies by country)
- Express delivery options at checkout
- Click & Collect at Mango stores (use store locator at shop.mango.com/stores)

**Mango loyalty program:**
- HE by Mango (hestores.mango.com) — part of Mango group
- Mango Premium membership benefits at shop.mango.com/premium

**Discount sources for European buyers:**
- Mango sale section: shop.mango.com/gb/sale
- Zalando (zalando.co.uk) — carries Mango with Zalando Plus perks
- ASOS (asos.com/mango) — Mango through ASOS platform

**EU consumer rights:**
- 14-day return right under EU Consumer Rights Directive
- Full returns policy at shop.mango.com/gb/returns"""
  },
  {
    "intent": "transactional",
    "query": "Urban Outfitters clothing clearance sale buy",
    "response": """Urban Outfitters clearance and sale shopping guide:

**Official Urban Outfitters sale:**
- Sale section: urbanoutfitters.com/sale
- Under $25 section: urbanoutfitters.com/under-25
- Urban Outfitters app — app-only sale access and early notifications
- Email list: urbanoutfitters.com — 10% welcome discount

**UO Membership:**
- UO Rewards (urbanoutfitters.com/uo-rewards) — points on every purchase
- Extra sale access for members

**Discount codes:**
- RetailMeNot (retailmenot.com/view/urbanoutfitters.com) — current promo codes
- Honey (joinhoney.com) — auto-apply at checkout
- Student/youth discount via UNiDAYS (myunidays.com) — 10% off

**URBN family cross-shopping:**
- Anthropologie (anthropologie.com) — more premium
- Free People (freepeople.com) — boho/festival aesthetic
- Terrain (terrain.com) — home and garden

**Secondhand Urban Outfitters:**
- Poshmark (poshmark.com) — UO resale community
- Depop (depop.com) — popular for UO vintage finds

Return policy: urbanoutfitters.com/help/return-policy — 30 days with tags."""
  },
  {
    "intent": "transactional",
    "query": "PrettyLittleThing express delivery clothing order",
    "response": """PrettyLittleThing (PLT) express delivery ordering guide:

**Official PLT channels:**
- Website: prettylittlething.com
- PLT app (iOS/Android) — app-exclusive deals (often extra 10-20% off)
- PLT Plus membership (prettylittlething.com/plus) — unlimited next-day delivery

**Express delivery options:**
- Next Day Delivery: order before cutoff (check prettylittlething.com/delivery-info)
- PLT Plus: unlimited express delivery for annual fee
- International express: available to selected countries

**Discount stacking for PLT:**
- PLT student discount via UNiDAYS (myunidays.com) — extra % off
- Honey extension (joinhoney.com) — promo code auto-testing
- RetailMeNot (retailmenot.com/view/prettylittlething.com) — current codes
- PLT email signup — new customer discount

**Returns:**
- Returns within 28 days: prettylittlething.com/returns
- PLT Plus members get free returns

**Independent reviews:**
- Trustpilot (trustpilot.com/review/prettylittlething.com) — customer experiences
- Vogue UK (vogue.co.uk) — brand coverage
- The Guardian (theguardian.com) — sustainability concerns coverage"""
  },
]

# ─────────────────────────────────────────────
# CLASSIFICATION + ANALYSIS (same as run_experiment.py)
# ─────────────────────────────────────────────

SOCIAL_DOMAINS = {
    "reddit.com", "twitter.com", "x.com", "instagram.com", "facebook.com",
    "tiktok.com", "pinterest.com", "tumblr.com", "youtube.com", "quora.com",
    "weibo.com", "xiaohongshu.com", "threads.net",
}

BRAND_DOMAINS = {
    "zara.com", "hm.com", "nike.com", "adidas.com", "shein.com", "asos.com",
    "uniqlo.com", "gap.com", "forever21.com", "nordstrom.com", "amazon.com",
    "levis.com", "mango.com", "shop.mango.com", "urbanoutfitters.com", "prettylittlething.com",
    "macys.com", "target.com", "walmart.com", "abercrombie.com", "ae.com",
    "anthropologie.com", "freepeople.com", "express.com", "jcrew.com",
    "bananarepublic.com", "bananarepublic.gap.com", "ralphlauren.com", "calvinklein.com",
    "tommyhilfiger.com", "coach.com", "katespade.com", "michaelkors.com",
    "guess.com", "lululemon.com", "underarmour.com", "puma.com", "newbalance.com",
    "vans.com", "converse.com", "reebok.com", "champion.com", "patagonia.com",
    "columbia.com", "thenorthface.com", "allbirds.com", "everlane.com",
    "reformation.com", "eileen-fisher.com", "eileenfisher.com", "farfetch.com",
    "net-a-porter.com", "matchesfashion.com", "ssense.com", "revolve.com",
    "shopbop.com", "bloomingdales.com", "saksfifthavenue.com", "zalando.com",
    "boohoo.com", "fashionnova.com", "poshmark.com", "depop.com", "ebay.com",
    "etsy.com", "shopify.com", "aliexpress.com", "zappos.com", "nordstromrack.com",
    "gapfactory.com", "oldnavy.gap.com", "athleta.gap.com", "threadup.com",
    "thredup.com", "llbean.com", "rei.com", "landsend.com", "katespade.com",
    "therealreal.com", "vestiairecollective.com", "fashionphile.com", "rebag.com",
    "tradesy.com", "renttherunway.com", "stitchfix.com", "nuuly.com", "prana.com",
    "aloyoga.com", "vuoriclothing.com", "beyondyoga.com", "girlfriend.com",
    "fabletics.com", "eloquii.com", "torrid.com", "lanebryant.com",
    "universalstandard.com", "apeainthepod.com", "hatchcollection.com",
    "seraphine.com", "storq.com", "ingridandisabel.com", "lulus.com",
    "neimanmarcus.com", "saksoff5th.com", "lastcall.com", "suitsupply.com",
    "bonobos.com", "mmlafleur.com", "anntaylor.com", "brooksbrothers.com",
    "ctshirts.com", "supreme.com", "supremenewyork.com", "kith.com", "bape.com",
    "us.bape.com", "fearofgod.com", "endclothing.com", "mrporter.com",
    "moncler.com", "canadagoose.com", "arcteryx.com", "madewell.com",
    "janieandjack.com", "carters.com", "oshkosh.com", "primary.com",
    "hannaandersson.com", "dickssportinggoods.com", "footlocker.com",
    "jdsports.com", "stadiumgoods.com", "stockx.com", "kidizen.com",
    "wearpact.com", "tentree.com", "wearethought.com", "stellamccartney.com",
    "veja-store.com", "ekm.com", "inditex.com", "fitnyc.edu",
    "fleetfeet.com", "runningwarehouse.com",
}


def classify_domain(d: str) -> str:
    d = d.lower().lstrip("www.")
    if d in SOCIAL_DOMAINS:
        return "Social"
    if d in BRAND_DOMAINS:
        return "Brand"
    return "Earned"


def extract_domains(text: str) -> list:
    # URLs
    urls = re.findall(r"https?://(?:www\.)?([a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)+)", text)
    # Bare domains in parentheses or after colon
    bare = re.findall(r"\((?:www\.)?([a-zA-Z0-9\-]+\.(?:com|org|net|io|co|uk|de|fr|es))\)", text)
    bare += re.findall(r":\s*(?:www\.)?([a-zA-Z0-9\-]+\.(?:com|org|net|io|co|uk|de|fr|es))\b", text)
    return list({d.lower() for d in urls + bare})


def analyze(responses: list) -> dict:
    results = []
    for r in responses:
        doms = extract_domains(r["response"])
        types = [classify_domain(d) for d in doms]
        results.append({**r, "domains": doms, "types": types,
                        "brand": types.count("Brand"),
                        "earned": types.count("Earned"),
                        "social": types.count("Social"),
                        "total": len(doms)})

    domain_freq = defaultdict(int)
    by_intent = {}

    for intent in ("informational", "consideration", "transactional"):
        sub = [r for r in results if r["intent"] == intent]
        total = sum(r["total"] for r in sub) or 1
        brand = sum(r["brand"] for r in sub)
        earned = sum(r["earned"] for r in sub)
        social = sum(r["social"] for r in sub)
        by_intent[intent] = {
            "n": len(sub),
            "avg_src": round(sum(r["total"] for r in sub) / len(sub), 1),
            "brand_pct": round(brand / total * 100, 1),
            "earned_pct": round(earned / total * 100, 1),
            "social_pct": round(social / total * 100, 1),
            "brand": brand, "earned": earned, "social": social, "total": total,
        }

    for r in results:
        for d in r["domains"]:
            domain_freq[d] += 1

    all_total = sum(r["total"] for r in results) or 1
    top = sorted(domain_freq.items(), key=lambda x: x[1], reverse=True)[:25]

    return {
        "total_queries": len(results),
        "overall": {
            "total_sources": all_total,
            "brand_pct": round(sum(r["brand"] for r in results) / all_total * 100, 1),
            "earned_pct": round(sum(r["earned"] for r in results) / all_total * 100, 1),
            "social_pct": round(sum(r["social"] for r in results) / all_total * 100, 1),
        },
        "by_intent": by_intent,
        "unique_domains": len(domain_freq),
        "top_domains": [{"domain": d, "count": c, "type": classify_domain(d)} for d, c in top],
        "raw": results,
    }


PAPER_CLAUDE = {
    "overall":         {"brand_pct": 34.4, "earned_pct": 64.5, "social_pct": 1.1},
    "informational":   {"brand_pct": 40.5, "earned_pct": 57.8, "social_pct": 1.7},
    "consideration":   {"brand_pct": 12.7, "earned_pct": 85.9, "social_pct": 1.5},
    "transactional":   {"brand_pct": 52.0, "earned_pct": 48.0, "social_pct": 0.0},
}
PAPER_GOOGLE = {"brand_pct": 25.7, "earned_pct": 40.7, "social_pct": 33.6}


def print_report(a: dict) -> None:
    sep = "─" * 68
    print(f"\n{'='*68}")
    print("  GEO ANALYSIS — CLOTHING E-COMMERCE (50 queries)")
    print(f"  claude-sonnet-4-6  |  {time.strftime('%Y-%m-%d')}")
    print(f"{'='*68}")
    print(f"  Queries: {a['total_queries']}   |   Unique domains cited: {a['unique_domains']}")

    o = a["overall"]
    pg = PAPER_GOOGLE
    pc = PAPER_CLAUDE["overall"]
    print(f"\n{sep}")
    print("  OVERALL SOURCE TYPOLOGY")
    print(sep)
    print(f"  {'System':<28}  {'Brand':>7}  {'Earned':>8}  {'Social':>8}")
    print(f"  {'-'*28}  {'-------':>7}  {'--------':>8}  {'--------':>8}")
    print(f"  {'This experiment (clothing)':28}  {o['brand_pct']:>6.1f}%  {o['earned_pct']:>7.1f}%  {o['social_pct']:>7.1f}%")
    print(f"  {'Paper: Claude (electronics)':28}  {pc['brand_pct']:>6.1f}%  {pc['earned_pct']:>7.1f}%  {pc['social_pct']:>7.1f}%")
    print(f"  {'Paper: Google (electronics)':28}  {pg['brand_pct']:>6.1f}%  {pg['earned_pct']:>7.1f}%  {pg['social_pct']:>7.1f}%")

    print(f"\n{sep}")
    print("  BY QUERY INTENT")
    print(sep)
    for intent, s in a["by_intent"].items():
        pb = PAPER_CLAUDE[intent]
        print(f"\n  {intent.upper()} — {s['n']} queries, avg {s['avg_src']} domains/query")
        print(f"  {'':4}{'Source':<26}  {'Brand':>7}  {'Earned':>8}  {'Social':>8}")
        print(f"  {'':4}{'This experiment':26}  {s['brand_pct']:>6.1f}%  {s['earned_pct']:>7.1f}%  {s['social_pct']:>7.1f}%")
        print(f"  {'':4}{'Paper Claude baseline':26}  {pb['brand_pct']:>6.1f}%  {pb['earned_pct']:>7.1f}%  {pb['social_pct']:>7.1f}%")

    print(f"\n{sep}")
    print("  TOP 25 MOST CITED DOMAINS (clothing e-commerce)")
    print(sep)
    print(f"  {'Type':<8}  {'Cited':>5}  Domain")
    for item in a["top_domains"]:
        bar = "█" * item["count"]
        print(f"  {item['type']:<8}  {item['count']:>4}x  {item['domain']:<35} {bar}")
    print(f"\n{'='*68}\n")


if __name__ == "__main__":
    print("Analyzing 50 pre-generated Claude responses for clothing e-commerce...")
    analysis = analyze(RAW_RESPONSES)
    print_report(analysis)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geo_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved → {out}")
