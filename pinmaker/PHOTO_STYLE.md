# Featured photo style (Lori's taste, learned by trial)

Featured images on ballenblogger.com are 16:9. Pins crop roughly the middle half,
so the subject sits in the center of the frame.

## Generator
Ideogram connector, `edit_images` with operation `edit_nano_banana_pro`
(`aspect_ratio` "16:9", `resolution_tier` "2K"). Ideogram 3.0 "realistic" read as
glossy and fake. Make one image at a time and refine with Lori.

## What she likes
- BIG IDEAS: every featured photo needs a magazine-worthy design idea, a wow factor that makes
  you stop scrolling (e.g. a color-drenched room, a painted arched alcove, a statement bed).
  The idea is magazine-level, but the photo still looks like a real snapshot, not a glossy render.
- A real snapshot: eye level, taken from a doorway or standing, slightly off-center.
- Bright and airy: daylight flooding in from windows just out of frame, no dark corners.
- Full and colorful but tidy, every item a recognizable real thing.
- Practical rooms: storage on the walls, nothing that wastes space.
- Believable proportions: normal ceiling height, a bit roomy, nothing too symmetrical.
- Clean floors.

- Millennial homes (her readers): modern-organic, light oak, rattan and cane, boucle, linen,
  arched mirrors, mushroom lamps, plants, Target/West Elm-style furniture, and real-life details
  like a TV on the dresser, a phone on the charger, a laundry basket.

## What she rejects
- Glossy "editorial / magazine" renders, CGI look, wide-angle distortion.
- Pegboards and other small-tool clutter (AI garbles them).
- A window behind the subject.
- Mess on the floor, even when added for "realism".
- Posters or wall art in working rooms like a craft room.
- Ornate vintage furniture and grandma styling when the post isn't about that look.
- Staged, impractical styling (candlesticks on a dresser, fancy fake furniture). Surfaces hold what
  a real person uses: jewelry dish, hairbrush, perfume, a plant, one vase of flowers.
- Chair-centered compositions (the armchairs come out weird). A plain chair tucked at a table is fine.
- Empty, sparse rooms.
- Plain, boring rooms (mint bedroom round 1: simple bed, plain mirror, one plant). Bedrooms need
  personality: layered bedding, a statement headboard or mirror, lots of flowers, color and pattern.

## Approved examples
- Craft room 100 (round 5): spacious, every wall storage, bright, chair pushed back from the table.
- Boho 100: candid sunlit living room, cream linen sofa, macrame, plants.

## Prompt skeleton
> A real photograph of a real person's {room}, taken standing at normal eye level with an
> iPhone, natural straight-on perspective, slightly off-center like a real snapshot.
> {subject and furniture, roomy}. {walls full of practical storage / styled items}.
> {table or surface details}. Very bright and airy, lots of soft daylight flooding in from
> big windows just out of frame on the left, no dark corners. {floor}, clean, nothing on the
> floor. Full, {mood} and inspiring but tidy and believable, ordinary real-home proportions,
> nothing too perfect or symmetrical. Natural bright exposure, natural colors, soft shadows,
> slight phone-camera grain, no CGI, no 3D render look, no wide-angle distortion. Wide
> horizontal frame. No window behind the subject, no text, no people.

## Standing rules from Lori
- Always fix typos you come across on her posts (titles, excerpts, alt text, pin copy). No need to ask.
- Always improve: every round should be better than the last, and each lesson gets written down here.

## Ideogram pins (whole pin made in Ideogram) — APPROVED STYLE
- The photo fills the whole pin edge to edge. Never a flat text block across the bottom
  (Lori: "too boring"; a tall panel also "cuts off too much of the picture").
- Text sits on a pretty soft cream rounded label floating over the bottom fifth of the photo,
  with a delicate blush double-line border and a tiny blush heart; the photo shows around it.
- Mixed fonts: the first words in an elegant flowing blush script ("The 7 Best"), the key
  words in bold espresso serif capitals with wide letter spacing ("DOG BEDS"), a tiny italic
  subline, and tiny sans-serif "ballenblogger.com". Chic boutique-brand feel.
- No tags or labels on objects (AI writes gibberish on them). Check spelling with
  describe_image and eyeball the Tailwind draft with get_post_image.
- Approved example: dog beds, Ideogram response DPqUuZnbUrWLwM7QqFv9-A (ideogram_3, realistic, 2x3).
- Keep the approved wording word for word ("Over the bottom fifth of the photo floats a pretty
  ... label ... so the picture shows around it on all sides"). Asking for a "small, compact label
  in only the bottom 20 percent" made Ideogram draw a flat full-width band instead.
- Flat lays and product scenes: say "all objects plain and unbranded, absolutely no writing on
  any object", or Ideogram prints gibberish brand names on boxes and cups.
- Featured images that are text graphics (title baked in) can't be used for the regular or
  B&W pins; those posts need a new featured photo first.

## Talking with Lori
- One thing at a time. Show one image or ask one question, then wait. No long status lists.
