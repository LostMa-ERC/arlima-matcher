import re

CenturyMap = (
    ("I", 0),
    ("II", 100),
    ("III", 200),
    ("IV", 300),
    ("V", 400),
    ("VI", 500),
    ("VII", 600),
    ("VIII", 700),
    ("IX", 800),
    ("X", 900),
    ("XI", 1000),
    ("XII", 1100),
    ("XIII", 1200),
    ("XIV", 1300),
    ("XV", 1400),
    ("XVI", 1500),
    ("XVII", 1600),
    ("XVII", 1700),
    ("XIX", 1800),
)


class DateParser:
    century = re.compile(r"([IVX]+)e\s|([IVX]+)\s|([IVX]+)$")
    first_half = re.compile(r"première moitié du ([IVX]+)[e\s$]", re.IGNORECASE)
    last_half = re.compile(r"seconde moitié du ([IVX]+)[e\s$]", re.IGNORECASE)
    before = re.compile(r"avant[\sle]+([XVI1-9]+)", re.IGNORECASE)

    def __init__(self) -> None:
        pass

    @staticmethod
    def convert_century(num: str) -> int:
        """Convert Roman numeral century to year integer.

        Examples:
            >>> DateParser.convert_century("XVI")
            1500

        Args:
            num (str): Roman numeral century.

        Returns:
            int: Year integer.
        """
        for s, i in CenturyMap:
            if s == num:
                return i

    @classmethod
    def find_centuries(cls, s: str) -> list[int]:
        """_summary_

        Examples:
            >>> DateParser.find_centuries("Du 1398 au début XV")
            [1400]

        Args:
            s (str): _description_

        Returns:
            list[str]: _description_
        """

        found_centuries = []
        centuries = cls.century.findall(s)
        for century in centuries:
            for group in century:
                if group != "":
                    found_centuries.append(cls.convert_century(group))
        return found_centuries

    @staticmethod
    def parse_int_strings(s: str) -> list[int]:
        """Extract integers from a string.

        Examples:
            >>> DateParser.parse_int_strings("De 1398 à 1401")
            [1398, 1401]
            >>> DateParser.parse_int_strings("Du XII au début XIII")
            []
            >>> DateParser.parse_int_strings("Du 1398 au début XV")
            [1398]

        Args:
            s (str): String potentially containing integers.

        Returns:
            list[int]: List of extracted integers.
        """
        parts = s.split()
        years = []
        for p in parts:
            try:
                int(p)
            except ValueError:
                continue
            else:
                years.append(int(p))
        return years

    def __call__(self, date_string: str) -> list:
        """Extract earliest and latest date from string.

        Examples:
            >>> p = DateParser()
            >>>
            >>> p("Première moitié du XIVe siècle")
            [1300, 1350]
            >>> p("première moitié du XIVe siècle")
            [1300, 1350]
            >>> p("seconde moitié du XIVe siècle")
            [1350, 1400]
            >>> p("Avant 1462")
            [1400, 1462]
            >>> p("Avant le XIIe")
            [1000, 1100]
            >>> p("Du 1398 au début XV")
            [1398, 1400]

        Args:
            date_string (str): String describing date information.

        Returns:
            list: Ordered list of earliest and latest date.
        """

        end = None
        start = None

        # If the description orients the range by the start of half a century
        if self.first_half.match(date_string):
            s = self.first_half.match(date_string).group(1)
            start = self.convert_century(s)
            end = start + 50

        # If the description orients the range by the end of half a century
        elif self.last_half.match(date_string):
            s = self.last_half.match(date_string).group(1)
            s = self.convert_century(s)
            end = s + 100
            start = end - 50

        # If the description orients the range by its end point
        elif self.before.match(date_string):
            s = self.before.match(date_string).group(1)
            try:
                end = int(s)
                start = int(s[:2] + "00")
            except ValueError:
                end = self.convert_century(s)
                start = end - 100

        # If the description is a single or list of dates
        elif not end or not start:
            # Try parsing roman numeral centuries
            centuries = self.find_centuries(date_string)
            # Try parsing years
            years = self.parse_int_strings(date_string)

            # If only one roman numeral was found, describe the century
            if len(centuries) == 1 and len(years) == 0:
                start = centuries[0]
                try:
                    end = start + 100
                except Exception as e:
                    print(centuries, years, date_string)
                    raise e
            # Otherwise, combine the parsed times and find the earliest and latest
            else:
                all_time_points = centuries + years
                if len(all_time_points) > 0:
                    start = min(all_time_points)
                    end = max(all_time_points)

        return sorted(set([start, end]))
