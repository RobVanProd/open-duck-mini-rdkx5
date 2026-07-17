# Frank Fu RDK-X5 Build Source Audit

Status: `HOLD_SOURCE_DOCUMENTS_NOT_MEASUREMENT_EVIDENCE`

Decision: `REQUIRE_AS_BUILT_MEASUREMENT`

## Question

Can Frank Fu's referenced RDK-X5 Open Duck material supply any of the 46
source-backed values required by the frozen real-build torso-COM measurement?

## Primary-source findings

Frank Fu's authored article states that its objective is to run Open Duck Mini
with an RDK-X5. Its RDK section changes the OS, Python environment,
dependencies and runtime directory. For physical construction it points back
to the upstream Open Duck repository and says the remaining steps are the same
as the Raspberry Pi process. It provides no RDK-X5 mount CAD, installed-board
mass, thermal-stack definition, battery variant, component X placement, common
datum or uncertainty.

Sources:

- authored mirror: https://dev.to/frankfu/understanding-reinforcement-learning-through-openduck-1if0
- canonical article: https://frankfu.blog/openai/understanding-reinforcement-learning-through-openduck/
- upstream hardware repository: https://github.com/apirrone/Open_Duck_Mini/tree/v2
- upstream assembly guide: https://github.com/apirrone/Open_Duck_Mini/blob/v2/docs/assembly_guide.md

The authored DEV article is article 3429639, published
2026-03-30T08:50:12Z with no recorded edit timestamp at audit time. Its API
payload exposed 44 URLs; the hardware link is the upstream stock repository.
The one non-emoji article image is a stock servo-ID CAD view (source SHA-256
`dd580a9e50de9f9c7c95d6cc68180efcf0f46a346738d1d0df6e7eff766afc71`),
not a measured RDK assembly.

The upstream `v2` hardware tree was pinned at commit
`b23317a485b3cec7d8417f352478778b3475173c` (2026-01-31T10:28:29Z). Its 436
paths contain zero filename paths matching `rdk` or `x5`. It contains the
stock `raspberrypizerow.part/.stl`, stock `board.part/.stl`, stock battery-pack
assets and Pi-oriented assembly instructions. The public Onshape mass-property
API requires authentication; more importantly, even stock part properties
would not establish Rob's installed RDK-X5, heatsink/mount, wiring or battery
configuration.

## Schema mapping

Fields promoted into
`real_build_torso_com_measurement_template.json`: **0 of 46**.

The sources establish only that an RDK-X5 runtime adaptation exists. They do
not establish the mass or placement of the actual build. Nominal product
weights, image-based scale inference, stock Pi geometry, and the compiled
stock torso inertia remain prohibited substitutes.

The real-build decision therefore remains
`HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`. This audit closes the hypothesis that
the Frank Fu article or its linked upstream repository already contains the
needed mechanical evidence. It authorizes no numerical COM estimate, model
correction, Gate 5, deployment, RDK-X5 access or robot use.

