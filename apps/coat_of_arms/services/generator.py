import random
from dataclasses import dataclass
from pathlib import Path

import svgwrite

# --- Heraldic constants ---
SHIELD_SHAPES = ["heater", "round", "kite"]
DIVISIONS = ["plain", "per pale", "per fess", "quarterly"]

TINCTURES = {
    "gules": "#d20f0f",  # red
    "azure": "#0033cc",  # blue
    "vert": "#228B22",  # green
    "purpure": "#800080",  # purple
    "sable": "#111111",  # black
    "or": "#ffd700",  # gold
    "argent": "#f0f0f0",  # silver/white
}

CHARGES = ["lion rampant", "eagle displayed", "cross pattee", "fleur-de-lis", "chevron", "bend"]

MOTTOS = [
    None,
    "Fortune favors the bold",
    "Honor and Glory",
    "By Steel and Faith",
    "Ever Forward",
]


@dataclass(kw_only=True)
class HeraldicShield:
    shape: str
    division: str
    tinctures: list[str]
    charges: list[str]
    motto: str | None = None


class CoatOfArmsGeneratorService:
    """Service for generating heraldic coat of arms shields as SVG files."""

    def process(self, *, output_path: str | Path = "shield.svg") -> Path:
        """
        Generate a coat of arms and save it as an SVG file.
        """
        shield = self._generate_shield()
        return self._render_shield_svg(shield=shield, output_path=output_path)

    def _generate_shield(self) -> HeraldicShield:
        """Generate a random heraldic shield with proper heraldic rules."""
        shape = random.choice(SHIELD_SHAPES)
        division = random.choice(DIVISIONS)
        tinctures = random.sample(list(TINCTURES.keys()), k=2)

        # Apply heraldic rule: no metal on metal, no color on color
        tinctures = self._apply_heraldic_rules(tinctures=tinctures)

        charges = random.sample(CHARGES, k=random.randint(1, 2))
        motto = random.choice(MOTTOS)

        return HeraldicShield(shape=shape, division=division, tinctures=tinctures, charges=charges, motto=motto)

    def _apply_heraldic_rules(self, *, tinctures: list[str]) -> list[str]:
        """
        Apply the rule of tincture: no metal on metal, no color on color.
        """
        metals = {"argent", "or"}
        colors = set(TINCTURES.keys()) - metals

        if tinctures[0] in metals and tinctures[1] in metals:
            tinctures[1] = random.choice(list(colors))
        elif tinctures[0] in colors and tinctures[1] in colors:
            tinctures[1] = random.choice(list(metals))

        return tinctures

    def _render_shield_svg(self, *, shield: HeraldicShield, output_path: str | Path) -> Path:
        """
        Render a heraldic shield to an SVG file.
        """
        output_path = Path(output_path)
        dwg = svgwrite.Drawing(str(output_path), size=("400px", "500px"))

        # Background color 1
        dwg.add(dwg.rect(insert=(0, 0), size=("400px", "500px"), fill=TINCTURES[shield.tinctures[0]]))

        # Division
        if shield.division == "per pale":
            dwg.add(dwg.rect(insert=("200px", 0), size=("200px", "500px"), fill=TINCTURES[shield.tinctures[1]]))
        elif shield.division == "per fess":
            dwg.add(dwg.rect(insert=(0, "250px"), size=("400px", "250px"), fill=TINCTURES[shield.tinctures[1]]))
        elif shield.division == "quarterly":
            dwg.add(dwg.rect(insert=(0, 0), size=("200px", "250px"), fill=TINCTURES[shield.tinctures[1]]))
            dwg.add(dwg.rect(insert=("200px", "250px"), size=("200px", "250px"), fill=TINCTURES[shield.tinctures[1]]))

        # Charges (text placeholders)
        for i, charge in enumerate(shield.charges):
            dwg.add(
                dwg.text(
                    charge, insert=("50%", f"{60 + i * 30}%"), text_anchor="middle", font_size="20px", fill="black"
                )
            )

        # Motto at bottom
        if shield.motto:
            dwg.add(
                dwg.text(
                    shield.motto,
                    insert=("50%", "95%"),
                    text_anchor="middle",
                    font_size="14px",
                    font_style="italic",
                    fill="black",
                )
            )

        dwg.save()
        return output_path
