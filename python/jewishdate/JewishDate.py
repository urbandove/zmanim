"""This is the module Docstring"""
from datetime import date, datetime, timedelta

NISSAN = 1
IYAR = 2
SIVAN = 3
TAMUZ = 4
AV = 5
ELUL = 6
TISHREI = 7
CHESHVAN = 8
KISLEV = 9
TEVES = 10
SHEVAT = 11
ADAR = 12
ADAR_II = 13
JEWISH_EPOCH = -1373429  # Jewish Epoch. Day 1 is Jan 1, 01 Gregorian. From Calendrical Calculations
CHALAKIM_PER_MINUTE = 18
CHALAKIM_PER_HOUR = 1080
CHALAKIM_PER_DAY = 25920 # 24 * 1080
CHALAKIM_PER_MONTH = 765433 # (29 * 24 + 12) * 1080 + 793
CHALAKIM_MOLAD_TOHU = 31524  # Chalakim from the beginning of Sunday till molad BaHaRaD.
CHASERIM = 0  # Cheshvan and Kislev both 29 days
KESIDRAN = 1  # Cheshvan 29 days and Kislev 30 days
SHELAIMIM = 2  # Cheshvan and Kislev both 30 days

def get_jcal_elapsed_days(year):
    """Returns the number of days elapsed from the Sunday prior to the start of the Jewish calendar
    to the mean conjunction of Tishri of the Jewish year.
    """
    # Jewish lunar month = 29 days, 12 hours and 793 chalakim
    # chalakim since Molad Tohu BeHaRaD - 1 day, 5 hours and 204 chalakim
    metonic_cycles, year_in_cycle = divmod(year - 1, 19)
    months = metonic_cycles * 235 # Months in complete 19 year lunar (Metonic) cycles so far
    months += year_in_cycle * 12 # Regular months in this cycle
    months += int((7 * year_in_cycle + 1) / 19) # Leap months this cycle
    months += get_jmonth_of_year(year, TISHREI) - 1  #  add months since start of year
    # return chalakim prior to BeHaRaD + number of chalakim since
    chalakim_since = CHALAKIM_MOLAD_TOHU + (CHALAKIM_PER_MONTH * months)
    rosh_hashana_day, molad_parts = divmod(chalakim_since, CHALAKIM_PER_DAY)
    # delay Rosh Hashana for the 4 dechiyos
    #roshHashanaDay = moladDay # if no dechiyos
    # delay Rosh Hashana for the dechiyos of the Molad - new moon
    # 1 - Molad Zaken, 2- GaTRaD 3- BeTuTaKFoT
    if molad_parts >= 19440: # Molad Zaken Dechiya - molad is >= midday (18 hours * 1080 chalakim)
        rosh_hashana_day += 1 # Then postpone Rosh HaShanah one day
    else:
        temp = rosh_hashana_day % 7
        if (((temp == 2) # start Dechiya of GaTRaD - Ga = is a Tuesday
             and (molad_parts >= 9924) # TRaD = 9 hours, 204 parts or later (9 * 1080 + 204)
             and (not is_jyear_leap(year))) # of a non-leap year - end Dechiya of GaTRaD
                or ((temp == 1) # start Dechiya of BeTuTaKFoT - Be = is on a Monday
                    and (molad_parts >= 16789) # TRaD >= 15 hours, 589 parts (15 * 1080 + 589)
                    and (is_jyear_leap(year - 1)))): # year following a leap year - no BeTuTaKFoT
            rosh_hashana_day += 1 # Then postpone Rosh HaShanah one day
    # start 4th Dechiya - Lo ADU Rosh - Rosh Hashana can't occur on A- Sun, D- Wed, U - Fri
    if rosh_hashana_day % 7 in {0, 3, 5}:# If RH would occur on Sun, Wed or Fri - Lo ADU Rosh
        rosh_hashana_day += 1 # Then postpone it one (more) day
    return rosh_hashana_day

def get_chalakim_since_molad_tohu(year, month):
    """Returns the number of chalakim (parts - 1080 to the hour) from the original hypothetical
    Molad Tohu to the year and month passed in.
    """
    # Jewish lunar month = 29 days, 12 hours and 793 chalakim
    # chalakim since Molad Tohu BeHaRaD - 1 day, 5 hours and 204 chalakim
    metonic_cycles, year_in_cycle = divmod(year - 1, 19)
    months = metonic_cycles * 235 # Months in complete 19 year lunar (Metonic) cycles so far
    months += year_in_cycle * 12 # Regular months in this cycle
    months += int((7 * year_in_cycle + 1) / 19) # Leap months this cycle
    months += get_jmonth_of_year(year, month) - 1  # add months since sstat of year
    # return chalakim prior to BeHaRaD + number of chalakim since
    return CHALAKIM_MOLAD_TOHU + (CHALAKIM_PER_MONTH * months)

def jdate_to_abs_date(year, month, day):
    """Returns the absolute date of Jewish date. ND+ER
    Arguments:
    year -- Jewish year. The year can't be negative
    month -- Nissan =1 and Adar II = 13
    day -- day of month
    """
    elapsed_days = day
    # Before Tishrei (from Nissan to Tishrei), add days in prior months
    if month < TISHREI:
        # this year before and after Nisan.
        for mon in range(TISHREI, getLastMonthOfJewishYear(year)+1):
            elapsed_days += get_days_in_jmonth(mon, year)
        for mon in range(NISSAN, month):
            elapsed_days += get_days_in_jmonth(mon, year)
    else: # Add days in prior months this year
        for mon in range(TISHREI, month):
            elapsed_days += get_days_in_jmonth(mon, year)
    # add elapsed days this year + Days in prior years + Days elapsed before absolute year 1
    return int(elapsed_days + get_jcal_elapsed_days(year) + JEWISH_EPOCH)

def getLastMonthOfJewishYear(year):
    """Return the last month of a given Jewish year. This will be 12 but 13 on leap year"""
    return ADAR_II if is_jyear_leap(year) else ADAR

def get_jmonth_of_year(year, month):
    """Converts the Nissan based months used by this class to numeric month starting from Tishrei.
    This is required for Molad claculations.
    """
    is_leap_year = is_jyear_leap(year)
    return (month + (6 if is_leap_year else 5)) % (13 if is_leap_year else 12) + 1

def get_days_in_jyear(year):
    """Returns the number of days for a given Jewish year. ND+ER"""
    return get_jcal_elapsed_days(year + 1) - get_jcal_elapsed_days(year)

def is_jyear_leap(year):
    """Return True if the year is a Jewish leap year.
    Years 3, 6, 8, 11, 14, 17 and 19 in the 19 year cycle are leap years.
    """
    return ((7 * year) + 1) % 19 < 7

def is_cheshvan_long(year):
    """Returns if Cheshvan is long in a given Jewish year."""
    return get_days_in_jyear(year) % 10 == 5

def is_kislev_short(year):
    """Returns if Kislev is short (29 days VS 30 days) in a given Jewish year."""
    return get_days_in_jyear(year) % 10 == 3

def get_days_cheshvan_kislev(year):
    """Returns a tuple containing (days_in_cheshvan, days_in_kislev) for given year"""
    days = get_days_in_jyear(year)
    cheshvandays = 29
    kislevdays = 30
    if days % 10 == 5:
        cheshvandays = 30
    if days % 10 == 3:
        kislevdays = 29
    return (cheshvandays, kislevdays)

def get_days_in_jmonth(month, year):
    """Returns the number of days of a Jewish month for a given month and year."""
    if (month == IYAR or month == TAMUZ
            or month == ELUL or month == TEVES
            or month == ADAR_II):
        return 29
    if ((month == CHESHVAN) and (not is_cheshvan_long(year)) or
            ((month == KISLEV) and is_kislev_short(year)) or
            ((month == ADAR) and (not is_jyear_leap(year)))):
        return 29
    return 30

def datetimeToJewishDate(dt):
    """Computes the Jewish date from the absolute date. ND+ER"""
    abs_date = dt.toordinal()
    # Start with approximation
    jyear = dt.year + 3760
    # Search forward for year from the approximation
    tempabsdate = jdate_to_abs_date(jyear + 1, TISHREI, 1)
    while abs_date >= tempabsdate:
        jyear += 1
        if abs_date - tempabsdate < 353:
            break
        tempabsdate = jdate_to_abs_date(jyear + 1, TISHREI, 1)
    is_leap_year = is_jyear_leap(jyear)
    #start with tishrei
    jmonth = TISHREI
    daysbeyond0ofjmonth = abs_date - jdate_to_abs_date(jyear, jmonth, 1)
    daysinjmonth = get_days_in_jmonth(jmonth, jyear)
    #go forward month by month
    while daysbeyond0ofjmonth >= daysinjmonth:
        jmonth += 1
        if jmonth > 12:
            if (not is_leap_year) or jmonth == 14:
                jmonth = 1
        daysbeyond0ofjmonth -= daysinjmonth
        if jmonth == CHESHVAN:
            cheshvandays, kislevdays = get_days_cheshvan_kislev(jyear)
            if daysbeyond0ofjmonth >= cheshvandays:
                jmonth += 1
                daysbeyond0ofjmonth -= cheshvandays
            if daysbeyond0ofjmonth >= kislevdays:
                jmonth += 1
                daysbeyond0ofjmonth -= kislevdays
        daysinjmonth = get_days_in_jmonth(jmonth, jyear)
    jday = daysbeyond0ofjmonth + 1
    return (jyear, jmonth, jday)

def validateJewishDate(year, month, day, hours=0, minutes=0, chalakim=0):
    """Validates the components of a Jewish date for validity. It will throw a ValueError if the
    Jewish date is earlier than 18 Teves, 3761 (1/1/1 Gregorian),
    a month < 1 or > 12 (or 13 on a leap year), the day of month is < 1 or > 30, an hour < 0
    or > 23, a minute < 0 > 59 or chalakim < 0 > 17. For a larger number of chalakim such
    as 793 (TaShTzaG) break the chalakim into minutes (18 chalakim per minutes, so it
    would be 44 minutes and 1 chelek in the case of 793/TaShTzaG).

    Arguments:
    year -- jewish year
    month -- jewish month
    day -- jewish day of month
    hours -- of molad - between 0 and 23
    minutes -- of molad - between 0 and 59
    chalakim -- of molad - between 0 and 17
    """
    if month < NISSAN or month > getLastMonthOfJewishYear(year):
        raise ValueError("""The Jewish month has to be between 1 and 12 (or 13 on a leap year).
                        %s is invalid for the year %s.""" % (month, year))
    if day < 1 or day > 30:
        raise ValueError("The Jewish day of month can't be < 1 or > 30.  %s is invalid." % (day))

    if day >= 29:
        if day > get_days_in_jmonth(month, year):
            raise ValueError("Day is out of range for month")

    # reject dates prior to 18 Teves, 3761 (1/1/1 AD). This restriction can be
    # relaxed if the date coding is changed/corrected
    if ((year < 3761) or
            (year == 3761 and (6 < month < TEVES or (month == TEVES and day < 18)))):
        raise ValueError("""A Jewish date earlier than 18 Teves, 3761 (1/1/1 Gregorian) can't
                            be set. %s, %s, %s  is invalid.""" % (year, month, day))


    if hours < 0 or hours > 23:
        raise ValueError("Hours < 0 > 23 can't be set. %s is invalid." % (hours))
    if minutes < 0 or minutes > 59:
        raise ValueError("Minutes < 0 > 59 can't be set. %s is invalid." % (minutes))
    if chalakim < 0 or chalakim > 17:
        raise ValueError("""Chalakim/parts < 0 > 17 can't be set. %s is invalid.
                         For larger numbers such as 793 (TaShTzaG) break the chalakim
                         into minutes (18 chalakim per minutes, so it would be 44 minutes and 1 chelek
                         in the case of 793 (TaShTzaG)""" % (chalakim))
    return (year, month, day, hours, minutes, chalakim)

class JewishDate(object):
    """Creates a Jewish date
    Arguments:
    year -- can be a datetime object - then all other arguments are disregarded
    year -- the Jewish year. The year can't be negative
    month -- the Jewish month. Nissan = 1 Adar II = 13
    day -- the Jewish day of month
    """

    NISSAN = 1
    IYAR = 2
    SIVAN = 3
    TAMUZ = 4
    AV = 5
    ELUL = 6
    TISHREI = 7
    CHESHVAN = 8
    KISLEV = 9
    TEVES = 10
    SHEVAT = 11
    ADAR = 12
    ADAR_II = 13
    JEWISH_EPOCH = -1373429  # Jewish Epoch. Day 1 is Jan 1, 01 Gregorian. From Calendrical Calcs
    CHALAKIM_PER_MINUTE = 18
    CHALAKIM_PER_HOUR = 1080
    CHALAKIM_PER_DAY = 25920 # 24 * 1080
    CHALAKIM_PER_MONTH = 765433 # (29 * 24 + 12) * 1080 + 793
    CHALAKIM_MOLAD_TOHU = 31524  # Chalakim from the beginning of Sunday till molad BaHaRaD.
    CHASERIM = 0  # Cheshvan and Kislev both 29 days
    KESIDRAN = 1  # Cheshvan 29 days and Kislev 30 days
    SHELAIMIM = 2  # Cheshvan and Kislev both 30 days

    def fromordinal(self, abs_date):
        """Computes the Gregorian date from the absolute date."""
        self.set_date(datetime.fromordinal(abs_date))

    def toordinal(self):
        """Returns the absolute date (days since January 1, 0001 on the Gregorian calendar)."""
        return self.dt.toordinal()

    def is_jyear_leap(self, year=None):
        """Return True if the year is a Jewish leap year.
        Years 3, 6, 8, 11, 14, 17 and 19 in the 19 year cycle are leap years.
        """
        if year:
            return is_jyear_leap(year)
        return is_jyear_leap(self._jyear)

    def get_days_in_jyear(self):
        """Returns the number of days for a given Jewish year. ND+ER"""
        return get_days_in_jyear(self._jyear)

    def is_cheshvan_long(self):
        """Returns if Cheshvan is long in set Jewish year."""
        return is_cheshvan_long(self._jyear)

    def is_kislev_short(self):
        """Returns if Kislev is short (29 days VS 30 days) in set Jewish year."""
        return is_kislev_short(self._jyear)

    def get_cheshvan_kislev_kviah(self):
        """Returns the Cheshvan and Kislev kviah (whether a Jewish year is short, regular or long).
        Returns 0 for Chaseirim, 1 for Kesidron, and 2 for Shleimim
        """
        cheshvan, kislev = get_days_cheshvan_kislev(self._jyear)
        total = cheshvan + kislev
        if total == 60:
            return self.SHELAIMIM
        elif total == 58:
            return self.CHASERIM
        else:
            return self.KESIDRAN

    def get_molad(self):
        """Return the molad for a given year and month (between this month and preceding month).
        Returns a JewishDate set to the date of the molad with the molad_hours, molad_minutes and
        molad_chalakim set. In the current implementation, it sets the molad time based on a
        midnight date rollover. This means that Rosh Chodesh Adar II, 5771 with a molad of 7
        chalakim past midnight on Shabbos 29 Adar I / March 5, 2011 12:00 AM and 7 chalakim,
        will have the following values: hours: 0, minutes: 0, Chalakim: 7.
        """
        molad_date = JewishDate.now()
        molad_date.set_jdate_by_molad(get_chalakim_since_molad_tohu(self._jyear, self._jmonth))
        if molad_date.molad_hours >= 6:
            molad_date.forward()
        molad_date._molad_hours = (molad_date.molad_hours + 18) % 24
        return molad_date

    def set_jdate_by_molad(self, molad):
        """Sets JewishDate based on a molad passed in. The molad would be the number of
        chalakim/parts starting at the begining of Sunday prior to the molad Tohu BeHaRaD
        (Be = Monday, Ha= 5 hours and Rad =204 chalakim/parts) - prior to the start of the
        Jewish calendar. BeHaRaD is 23:11:20 on Sunday night(5 hours 204/1080 chalakim after
        sunset on Sunday evening).
        """
        molad_abs_day, chalakim = divmod(molad, self.CHALAKIM_PER_DAY)
        self.fromordinal(molad_abs_day + self.JEWISH_EPOCH) #maybe - jewihs epoch?
        self._molad_hours, chalakim = divmod(chalakim, self.CHALAKIM_PER_HOUR)
        self._molad_minutes, self._molad_chalakim = divmod(chalakim, self.CHALAKIM_PER_MINUTE)
        self.dt = (self.dt.replace(hours=self._molad_hours, minutes=self._molad_minutes,
                                   seconds=int(self._molad_chalakim * 3.33)))

    @property
    def molad_hours(self):
        """Molad Hours. Returns None if not set"""
        return self._molad_hours

    @property
    def molad_minutes(self):
        """Molad Minutes. Returns None if not set"""
        return self._molad_minutes

    @property
    def molad_chalakim(self):
        """Molad Chalakim. Returns None if not set"""
        return self._molad_chalakim

    def __init__(self, jyear, jmonth=None, jday=None):
        if isinstance(jyear, datetime) or isinstance(jyear, date):
            self.set_date(jyear)
        else:
            self.set_jdate(jyear, jmonth, jday)

    def set_date(self, datetime):
        """Sets the date based on datetime object. Modifies the Jewish date as well."""
        self.dt = datetime
        self._jyear, self._jmonth, self._jday = datetimeToJewishDate(datetime)

    def set_gdate(self, year=None, month=None, day=None, hour=0,
                  minute=0, second=0, microsecond=0):
        """Return a new JewishDate with new values for the specified fields. given in gregorian"""
        self.set_date(datetime(year, month, day, hour, minute, second, microsecond))

    def set_jdate(self, year, month, day, hours=None, minutes=None, chalakim=None):
        """Sets the Jewish Date and updates the Gregorian date accordingly.

        Arguments:
        year -- the Jewish year. The year can't be negative
        month -- the Jewish month. Nissan = 1 Adar II = 13
        day -- the Jewish day of month
        hours -- the hour of the day. Used for Molad calculations
        minutes -- the minutes. Used for Molad calculations
        chalakim -- the chalakim/parts. Used for Molad calculations. munt be less than 17

        raises a ValueError if a A Jewish date earlier than 18 Teves, 3761 (1/1/1 Gregorian),
        a month < 1 or > 12 (or 13 in a leap year), the day of month is < 1 or > 30,
        an hour < 0 or > 23, a minute < 0 > 59 or chalakim < 0 > 17. For larger a larger number
        of chalakim such as 793 (TaShTzaG) break the chalakim into minutes (18 chalakim per
        minutes, so it would be 44 minutes and 1 chelek in the case of 793 (TaShTzaG).
        """
        if not hours:
            validateJewishDate(year, month, day, 0, 0, 0)
        else:
            validateJewishDate(year, month, day, hours, minutes, chalakim)

        self._molad_hours = hours
        self._molad_minutes = minutes
        self._molad_chalakim = chalakim

        abs_date = jdate_to_abs_date(year, month, day) # reset Gregorian date
        self.dt = datetime.fromordinal(abs_date)
        self._jyear = year
        self._jmonth = month
        self._jday = day

    @classmethod
    def now(cls):
        """Creates Jewish Date set to current system time"""
        return JewishDate(datetime.now())

    def __str__(self):
        """Returns a string containing the Jewish date in the form, "day Month, year"
        e.g. "21 Shevat, 5729". For more complex formatting, use the formatter classes.
        """
        from .HebrewDateFormatter import HebrewDateFormatter
        return HebrewDateFormatter().format_date(self)

    def format(self, format_string):
        from .HebrewDateFormatter import HebrewDateFormatter
        return HebrewDateFormatter().format(self, format_string)

    def strftime(self, format_string):
        from .HebrewDateFormatter import HebrewDateFormatter
        return HebrewDateFormatter().format(self, format_string)

    @property
    def heb_string(self):
        """Returns a string containing the Jewish date in the form, "day Month, year"
        e.g. "21 Shevat, 5729". For more complex formatting, use the formatter classes.
        """
        from .HebrewDateFormatter import HebrewDateFormatter
        return HebrewDateFormatter(hebrew=True).format_date(self)

    def forward(self):
        """Rolls Date forward 1 day"""
        self.dt += timedelta(days=1)
        if self._jday < 29:
            self._jday += 1
        elif self._jday == get_days_in_jmonth(self._jmonth, self._jyear):
            self._jday = 1
            if self._jmonth == 6:
                self._jyear += 1
                self._jmonth = 7
            elif self._jmonth == 12:
                if self.is_jyear_leap():
                    self._jmonth = 13
                else:
                    self._jmonth = 1
            elif self._jmonth == 13:
                self._jmonth = 1
            else:
                self._jmonth += 1
        elif self._jday == 29:
            self._jday += 1
        else:
            raise ValueError("Date is Wrong")

    def back(self):
        """Rolls Date back 1 day"""
        self.dt -= timedelta(days=1)
        if self._jday > 1:
            self._jday -= 1
        else:
            if self._jmonth == 7:
                self._jyear -= 1
                self._jmonth -= 1
            elif self._jmonth == 1:
                if self.is_jyear_leap():
                    self._jmonth = 13
                else:
                    self._jmonth = 12
            else:
                self._jmonth -= 1
            self._jday = get_days_in_jmonth(self._jmonth, self._jyear)

    @property
    def gyear(self):
        """Gregorian Year"""
        return self.dt.year

    @property
    def gmonth(self):
        """Gregorian Month"""
        return self.dt.month

    @property
    def gday(self):
        """Gregorian Day"""
        return self.dt.day

    @property
    def jyear(self):
        """Jewish Year"""
        return self._jyear

    @property
    def jmonth(self):
        """Jewish Month - Nissan = 1, Adar II = 13"""
        return self._jmonth

    @property
    def jday(self):
        """Jewish Day"""
        return self._jday

    @property
    def dayofweek(self):
        """Day of the week as a number between Sunday=1, Saturday=7."""
        if self.dt.isoweekday() == 7:
            return 1
        return self.dt.isoweekday() + 1

    def get_days_in_month(self):
        return get_days_in_jmonth(self._jyear, self._jmonth)

    def isoweekday(self):
        """Return the day of the week as a number between Monday=1, Sunday=7."""
        return self.dt.isoweekday()

    def weekday(self):
        """Return datetime.weekday()"""
        return self.dt.weekday()

    def greplace(self, year=None, month=None, day=None, hour=None,
                 minute=None, second=None, microsecond=None, tzinfo=True):
        """Return a new JewishDate with new values for the specified fields. given in gregorian"""
        return JewishDate(self.dt.replace(year, month, day, hour,
                                          minute, second, microsecond, tzinfo))

    def jreplace(self, jyear=None, jmonth=None, jday=None):
        """Return a new JewishDate with new values for the specified fields.
        jyear -- must be between greater than 3761 (or 3761 if after 18 Teves)
        jmonth -- Nissan = 1 and Adar II = 13
        jday -- the day of the month
        """
        if not jyear:
            jyear = self._jyear
        if not jmonth:
            jmonth = self._jmonth
        if not jday:
            jday = self._jday
        return JewishDate(jyear, jmonth, jday)

SAT_SHORT = [None, 52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
             17, 18, 19, 20, 53, 23, 24, None, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38, 39,
             40, 58, 43, 44, 45, 46, 47, 48, 49, 50]
SAT_LONG = [None, 52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 53, 23, 24, None, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38, 39,
            40, 58, 43, 44, 45, 46, 47, 48, 49, 59]
MON_SHORT = [51, 52, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
             18, 19, 20, 53, 23, 24, None, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38, 39, 40,
             58, 43, 44, 45, 46, 47, 48, 49, 59]
MON_LONG = [51, 52, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            20, 53, 23, 24, None, 25, 54, 55, 30, 56, 33, None, 34, 35, 36, 37, 57, 40, 58, 43,
            44, 45, 46, 47, 48, 49, 59] #split
THU_NORMAL = [52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
              18, 19, 20, 53, 23, 24, None, None, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38,
              39, 40, 58, 43, 44, 45, 46, 47, 48, 49, 50]
THU_NORMAL_ISRAEL = [52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                     16, 17, 18, 19, 20, 53, 23, 24, None, 25, 54, 55, 30, 31, 32, 33, 34, 35,
                     36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47, 48, 49, 50]
THU_LONG = [52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
            18, 19, 20, 21, 22, 23, 24, None, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38,
            39, 40, 58, 43, 44, 45, 46, 47, 48, 49, 50]
SAT_SHORT_LEAP = [None, 52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                  16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, None, 28, 29, 30, 31, 32, 33,
                  34, 35, 36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47, 48, 49, 59]
SAT_LONG_LEAP = [None, 52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, None, 28, 29, 30, 31, 32, 33, None,
                 34, 35, 36, 37, 57, 40, 58, 43, 44, 45, 46, 47, 48, 49, 59]
MON_SHORT_LEAP = [51, 52, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                  17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, None, 28, 29, 30, 31, 32, 33,
                  None, 34, 35, 36, 37, 57, 40, 58, 43, 44, 45, 46, 47, 48, 49, 59]
MON_SHORT_LEAP_ISRAEL = [51, 52, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                         17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, None, 28, 29, 30, 31, 32,
                         33, 34, 35, 36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47, 48, 49, 59]
MON_LONG_LEAP = [51, 52, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                 19, 20, 21, 22, 23, 24, 25, 26, 27, None, None, 28, 29, 30, 31, 32, 33, 34, 35,
                 36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47, 48, 49, 50]
MON_LONG_LEAP_ISRAEL = [51, 52, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                        17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, None, 28, 29, 30, 31, 32, 33,
                        34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
THU_SHORT_LEAP = [52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                  17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, None, 29, 30, 31, 32, 33,
                  34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
THU_LONG_LEAP = [52, None, None, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, None, 29, 30, 31, 32, 33,
                 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 59]

PARSHA_ARRAY_DIASPORA = {(2, CHASERIM, False): MON_SHORT,
                         (2, SHELAIMIM, False): MON_LONG,
                         (3, KESIDRAN, False): MON_LONG,
                         (5, KESIDRAN, False): THU_NORMAL,
                         (5, SHELAIMIM, False): THU_LONG,
                         (7, CHASERIM, False): SAT_SHORT,
                         (7, SHELAIMIM, False): SAT_LONG,
                         (2, CHASERIM, True): MON_SHORT_LEAP,
                         (2, SHELAIMIM, True): MON_LONG_LEAP,
                         (3, KESIDRAN, True): MON_LONG_LEAP,
                         (5, CHASERIM, True): THU_SHORT_LEAP,
                         (5, SHELAIMIM, True): THU_LONG_LEAP,
                         (7, CHASERIM, True): SAT_SHORT_LEAP,
                         (7, SHELAIMIM, True): SAT_LONG_LEAP}

PARSHA_ARRAY_ISRAEL = {(2, CHASERIM, False): MON_SHORT,
                       (2, SHELAIMIM, False): MON_SHORT,
                       (3, KESIDRAN, False): MON_SHORT,
                       (5, KESIDRAN, False): THU_NORMAL_ISRAEL,
                       (5, SHELAIMIM, False): THU_LONG,
                       (7, CHASERIM, False): SAT_SHORT,
                       (7, SHELAIMIM, False): SAT_LONG,
                       (2, CHASERIM, True): MON_SHORT_LEAP_ISRAEL,
                       (2, SHELAIMIM, True): MON_LONG_LEAP_ISRAEL,
                       (3, KESIDRAN, True): MON_LONG_LEAP_ISRAEL,
                       (5, CHASERIM, True): THU_SHORT_LEAP,
                       (5, SHELAIMIM, True): THU_LONG_LEAP,
                       (7, CHASERIM, True): SAT_SHORT_LEAP,
                       (7, SHELAIMIM, True): SAT_SHORT_LEAP}

HOLIDAYS_DIASPORA = {(1, 14): 0,  # EREV_PESACH
                     (1, 15): 1,  # PESACH
                     (1, 16): 1,  # PESACH
                     (1, 17): 2,  # CHOL_HAMOED_PESACH
                     (1, 18): 2,  # CHOL_HAMOED_PESACH
                     (1, 19): 2,  # CHOL_HAMOED_PESACH
                     (1, 20): 2,  # CHOL_HAMOED_PESACH
                     (1, 21): 1,  # PESACH
                     (1, 22): 1,  # PESACH
                     (2, 14): 3,  # PESACH_SHENI
                     (2, 18): 33,  # LAG_BAOMER
                     (3, 5): 4,  # EREV_SHAVUOS
                     (3, 6): 5,  # SHAVUOS
                     (3, 7): 5,  # SHAVUOS
                     (5, 15): 8,  # TU_BEAV
                     (6, 29): 9,  # EREV_ROSH_HASHANA
                     (7, 1): 10,  # ROSH_HASHANA
                     (7, 2): 10,  # ROSH_HASHANA
                     (7, 9): 12,  # EREV_YOM_KIPPUR
                     (7, 10): 13,  # YOM_KIPPUR
                     (7, 14): 14,  # EREV_SUCCOS
                     (7, 15): 15,  # SUCCOS
                     (7, 16): 15,  # SUCCOS
                     (7, 17): 16,  # CHOL_HAMOED_SUCCOS
                     (7, 18): 16,  # CHOL_HAMOED_SUCCOS
                     (7, 19): 16,  # CHOL_HAMOED_SUCCOS
                     (7, 20): 16,  # CHOL_HAMOED_SUCCOS
                     (7, 21): 17,  # HOSHANA_RABBA
                     (7, 22): 18,  # SHEMINI_ATZERES
                     (7, 23): 19,  # SIMCHAS_TORAH
                     #(9, 24): 20,  # EREV_CHANUKAH
                     (9, 25): 21,  # CHANUKAH
                     (9, 26): 21,  # CHANUKAH
                     (9, 27): 21,  # CHANUKAH
                     (9, 28): 21,  # CHANUKAH
                     (9, 29): 21,  # CHANUKAH
                     (9, 30): 21,  # CHANUKAH - Though doesnt always exist - it is always chanuka
                     (10, 1): 21,  # CHANUKAH
                     (10, 2): 21,  # CHANUKAH
                     (10, 10): 22,  # TENTH_OF_TEVES
                     (11, 15): 23,  # TU_BESHEVAT
                     (13, 14): 25,  # PURIM
                     (13, 15): 26}  # SHUSHAN_PURIM

HOLIDAYS_ISRAEL = {(1, 14): 0,  # EREV_PESACH
                   (1, 15): 1,  # PESACH
                   (1, 16): 2,  # CHOL_HAMOED_PESACH
                   (1, 17): 2,  # CHOL_HAMOED_PESACH
                   (1, 18): 2,  # CHOL_HAMOED_PESACH
                   (1, 19): 2,  # CHOL_HAMOED_PESACH
                   (1, 20): 2,  # CHOL_HAMOED_PESACH
                   (1, 21): 1,  # PESACH
                   (2, 14): 3,  # PESACH_SHENI
                   (2, 18): 33,  # LAG_BAOMER
                   (3, 5): 4,  # EREV_SHAVUOS
                   (3, 6): 5,  # SHAVUOS
                   (5, 15): 8,  # TU_BEAV
                   (6, 29): 9,  # EREV_ROSH_HASHANA
                   (7, 1): 10,  # ROSH_HASHANA
                   (7, 2): 10,  # ROSH_HASHANA
                   (7, 9): 12,  # EREV_YOM_KIPPUR
                   (7, 10): 13,  # YOM_KIPPUR
                   (7, 14): 14,  # EREV_SUCCOS
                   (7, 15): 15,  # SUCCOS
                   (7, 16): 16,  # CHOL_HAMOED_SUCCOS
                   (7, 17): 16,  # CHOL_HAMOED_SUCCOS
                   (7, 18): 16,  # CHOL_HAMOED_SUCCOS
                   (7, 19): 16,  # CHOL_HAMOED_SUCCOS
                   (7, 20): 16,  # CHOL_HAMOED_SUCCOS
                   (7, 21): 17,  # HOSHANA_RABBA
                   (7, 22): 18,  # SHEMINI_ATZERES
                   #(9, 24): 20,  # EREV_CHANUKAH
                   (9, 25): 21,  # CHANUKAH
                   (9, 26): 21,  # CHANUKAH
                   (9, 27): 21,  # CHANUKAH
                   (9, 28): 21,  # CHANUKAH
                   (9, 29): 21,  # CHANUKAH
                   (9, 30): 21,  # CHANUKAH - Though doesnt always exist - it is always chanuka
                   (10, 1): 21,  # CHANUKAH
                   (10, 2): 21,  # CHANUKAH
                   (10, 10): 22,  # TENTH_OF_TEVES
                   (11, 15): 23,  # TU_BESHEVAT
                   (13, 14): 25,  # PURIM
                   (13, 15): 26}  # SHUSHAN_PURIM

FAST_DAYS_NIDCHE = {(4, 18, 1): 6,  # SEVENTEEN_OF_TAMMUZ
                    (5, 10, 1): 7,  # TISHA_BEAV
                    (7, 4, 1): 11,  # FAST_OF_GEDALYAH
                    (13, 11, 5): 24,  # FAST_OF_ESTHER
                    (13, 12, 5): 24}  # FAST_OF_ESTHER

FAST_DAYS_NORMAL = {(4, 17): 6,  # SEVENTEEN_OF_TAMMUZ
                    (5, 9): 7,  # TISHA_BEAV
                    (7, 3): 11,  # FAST_OF_GEDALYAH
                    (13, 13): 24}  # FAST_OF_ESTHER

MODERN_HOLIDAYS = {(1, 26, 5): 29,  # YOM_HASHOAH
                   (1, 27, 3): 29,  # YOM_HASHOAH
                   (1, 27, 7): 29,  # YOM_HASHOAH
                   (1, 28, 3): 29,  # YOM_HASHOAH
                   (2, 2, 4): 30,  # YOM_HAZIKARON
                   (2, 3, 4): 30,  # YOM_HAZIKARON
                   (2, 4, 3): 30,  # YOM_HAZIKARON
                   (2, 5, 2): 30,  # YOM_HAZIKARON
                   (2, 3, 5): 31,  # YOM_HAATZMAUT
                   (2, 4, 5): 31,  # YOM_HAATZMAUT
                   (2, 5, 4): 31,  # YOM_HAATZMAUT
                   (2, 6, 3): 31,  # YOM_HAATZMAUT
                   (2, 28, 1): 32,  # YOM_YERUSHALAYIM
                   (2, 28, 2): 32,  # YOM_YERUSHALAYIM
                   (2, 28, 3): 32,  # YOM_YERUSHALAYIM
                   (2, 28, 4): 32,  # YOM_YERUSHALAYIM
                   (2, 28, 5): 32,  # YOM_YERUSHALAYIM
                   (2, 28, 6): 32,  # YOM_YERUSHALAYIM
                   (2, 28, 7): 32}  # YOM_YERUSHALAYIM
EREV_PESACH = 0
PESACH = 1
CHOL_HAMOED_PESACH = 2
PESACH_SHENI = 3
EREV_SHAVUOS = 4
SHAVUOS = 5
SEVENTEEN_OF_TAMMUZ = 6
TISHA_BEAV = 7
TU_BEAV = 8
EREV_ROSH_HASHANA = 9
ROSH_HASHANA = 10
FAST_OF_GEDALYAH = 11
EREV_YOM_KIPPUR = 12
YOM_KIPPUR = 13
EREV_SUCCOS = 14
SUCCOS = 15
CHOL_HAMOED_SUCCOS = 16
HOSHANA_RABBA = 17
SHEMINI_ATZERES = 18
SIMCHAS_TORAH = 19
# EREV_CHANUKAH = 20# probably remove this
CHANUKAH = 21
TENTH_OF_TEVES = 22
TU_BESHEVAT = 23
FAST_OF_ESTHER = 24
PURIM = 25
SHUSHAN_PURIM = 26
PURIM_KATAN = 27
ROSH_CHODESH = 28
YOM_HASHOAH = 29
YOM_HAZIKARON = 30
YOM_HAATZMAUT = 31
YOM_YERUSHALAYIM = 32
LAG_BAOMER = 33
DAF_YOMI_START_DATE = datetime(1923, 9, 11)
SHEKALIM_CHANGE_DATE = datetime(1975, 6, 24)


class JewishCalendar(JewishDate):
    """Creates a Jewish Calendar object which extends the JewishDate class

    Arguments:
    year -- can be a datetime object - then all other arguments are disregarded
    year -- the Jewish year. The year can't be negative
    month -- the Jewish month. Nissan = 1 Adar II = 13
    day -- the Jewish day of month

    This open source Python code was originally ported to Java by
    <a href="http//www.facebook.com/avromf">Avrom Finkelstien</a> rom his C++ code.
    It was refactored to fit the KosherJava Zmanim API with simplification of the code,
    enhancements and some bug fixing. It was then ported to Python.
    The methods used to obtain the parsha were derived from the source code of
    <a href="http//www.sadinoff.com/hebcal/">HebCal</a> by Danny Sadinoff and JCal for
    the Mac by Frank Yellin. Both based their code on routines by Nachum Dershowitz
    and Edward M. Reingold. The class allows setting whether the parsha and holiday scheme
    follows the Israel scheme or outside Israel scheme. The default is the outside Israel scheme.

    TODO: Some do not belong in this class, but here is a partial list of what should still be
    implemented in some form:
    * Add Isru Chag
    * Add special parshiyos (shekalim, parah, zachor and hachodesh
    * Shabbos Mevarchim
    * Haftorah (various minhagim)
    * Daf Yomi Yerushalmi, Mishna yomis etc)
    * Support showing the upcoming parsha for the middle of the week

    Author: Avrom Finkelstien 2002
    Author: Eliyahu Hershfeld 2011 - 2012
    Version: 0.0.1
    """

    EREV_PESACH = 0
    PESACH = 1
    CHOL_HAMOED_PESACH = 2
    PESACH_SHENI = 3
    EREV_SHAVUOS = 4
    SHAVUOS = 5
    SEVENTEEN_OF_TAMMUZ = 6
    TISHA_BEAV = 7
    TU_BEAV = 8
    EREV_ROSH_HASHANA = 9
    ROSH_HASHANA = 10
    FAST_OF_GEDALYAH = 11
    EREV_YOM_KIPPUR = 12
    YOM_KIPPUR = 13
    EREV_SUCCOS = 14
    SUCCOS = 15
    CHOL_HAMOED_SUCCOS = 16
    HOSHANA_RABBA = 17
    SHEMINI_ATZERES = 18
    SIMCHAS_TORAH = 19
    # EREV_CHANUKAH = 20# probably remove this
    CHANUKAH = 21
    TENTH_OF_TEVES = 22
    TU_BESHEVAT = 23
    FAST_OF_ESTHER = 24
    PURIM = 25
    SHUSHAN_PURIM = 26
    PURIM_KATAN = 27
    ROSH_CHODESH = 28
    YOM_HASHOAH = 29
    YOM_HAZIKARON = 30
    YOM_HAATZMAUT = 31
    YOM_YERUSHALAYIM = 32
    LAG_BAOMER = 33
    DAF_YOMI_START_DATE = datetime(1923, 9, 11)
    SHEKALIM_CHANGE_DATE = datetime(1975, 6, 24)

    in_israel = False
    use_modern_holidays = False
    holiday_index = None
    not_holiday = False  # only for optimization - will not always be correct

    def __init__(self, date=datetime.now(), jmonth=None, jday=None, inisrael=False):
        super(JewishCalendar, self).__init__(date, jmonth, jday)
        self.in_israel = inisrael
        self.not_holiday = False
        self.holiday_index = None

    @classmethod
    def now(cls):
        """Creates Jewish Calendar set to current system time"""
        return JewishCalendar(datetime.now())

    def set_jdate_by_molad(self, molad):
        super(JewishCalendar, self).set_jdate_by_molad(molad)
        self.not_holiday = False
        self.holiday_index = None

    def set_date(self, dt):
        super(JewishCalendar, self).set_date(dt)
        self.not_holiday = False
        self.holiday_index = None

    def set_gdate(self, year=None, month=None, day=None, hour=0,
                  minute=0, second=0, microsecond=0):
        super(JewishCalendar, self).set_gdate(year, month, day, hour,
                                              minute, second, microsecond)
        self.not_holiday = False
        self.holiday_index = None

    def set_jdate(self, year, month, day, hours=None, minutes=None, chalakim=None):
        super(JewishCalendar, self).set_jdate(
            year, month, day, hours, minutes, chalakim)
        self.not_holiday = False
        self.holiday_index = None

    def forward(self):
        super(JewishCalendar, self).forward()
        self.not_holiday = False
        self.holiday_index = None

    def back(self):
        super(JewishCalendar, self).back()
        self.not_holiday = False
        self.holiday_index = None

    def get_yom_tov_index(self):
        """Return an index if current day is a Jewish holiday/fast day, or None if not"""
        if self.not_holiday:
            return None
        if self.holiday_index:
            return self.holiday_index
        if not self.in_israel:
            index = HOLIDAYS_DIASPORA.get((self.jmonth, self.jday), None)
        else:
            index = HOLIDAYS_ISRAEL.get((self.jmonth, self.jday), None)
        index = FAST_DAYS_NIDCHE.get((self.jmonth, self.jday, self.dayofweek), index)
        if not index:  # can probably be made into one line
            index = FAST_DAYS_NORMAL.get((self.jmonth, self.jday), None)
        if self.use_modern_holidays:
            index = MODERN_HOLIDAYS.get((self.jmonth, self.jday, self.dayofweek), index)
        if not index:
            if self.jmonth == TEVES:
                if self.is_kislev_short() and self.jday == 3:
                    index = CHANUKAH
            if self.jmonth == ADAR and not self.is_jyear_leap():
                if (self.jday == 11 or self.jday == 12 and self.dayofweek == 5
                        or self.jday == 13 and self.dayofweek < 6):
                    index = FAST_OF_ESTHER
                if self.jday == 14:
                    index = PURIM
                if self.jday == 15:
                    index = SHUSHAN_PURIM
            elif self.jmonth == ADAR and self.is_jyear_leap():
                if self.jday == 14:
                    index = PURIM_KATAN
            if not index: # still not a holiday
                self.not_holiday = True
                return None  # no Yom Tov
        self.holiday_index = index
        return index

    def is_yom_tov(self):
        """Return true if current day is Yom Tov. False for Chanukah, Erev Yom tov and fast days."""
        holiday_index = self.get_yom_tov_index()
        if (self.is_erev_yom_tov() or holiday_index == CHANUKAH
                or (self.is_taanis() and not holiday_index == YOM_KIPPUR)):
            return False
        return not holiday_index

    def is_chol_hamoed(self):
        """Return True if the current day is Chol Hamoed of Pesach or Succos."""
        holiday_index = self.get_yom_tov_index()
        return holiday_index == CHOL_HAMOED_PESACH or holiday_index == CHOL_HAMOED_SUCCOS

    def is_erev_yom_tov(self):
        """Return True if current day is erev Yom Tov. Returns true for Erev Pesach, Shavuos, Rosh
        Hashana, Yom Kippur and Succos.
        """
        holiday_index = self.get_yom_tov_index()
        return holiday_index in (EREV_PESACH, EREV_SHAVUOS,
                                 EREV_ROSH_HASHANA, EREV_YOM_KIPPUR, EREV_SUCCOS)

    def is_erev_rosh_chodesh(self):
        """Return True if the current day is Erev Rosh Chodesh. False for Erev Rosh Hashana"""
        return self.jday == 29 and self.jmonth != ELUL

    def is_taanis(self):
        """Return True if the day is a Taanis (fast day)."""
        holiday_index = self.get_yom_tov_index()
        return holiday_index in (SEVENTEEN_OF_TAMMUZ, TISHA_BEAV,
                                 YOM_KIPPUR, FAST_OF_GEDALYAH, TENTH_OF_TEVES, FAST_OF_ESTHER)

    def get_day_of_chanukah(self):
        """Returns the day of Chanukah or None if it is not Chanukah."""
        if self.is_chanukah():
            if self.jmonth == KISLEV:
                return self.jday - 24
            else: # teves
                if self.is_kislev_short():
                    return self.jday + 5
                return self.jday + 6
        return None

    def is_chanukah(self):
        """Returns True if its Chanukah"""
        return self.get_yom_tov_index() == CHANUKAH

    def get_parsha_index(self):
        """Return a the index of today's parsha(ios) or a -1 if there is none. To get the
        name of the Parsha, use the HebrewDateFormatter

        NOTE: This only returns the parsha for Shabbos - not the upcoming shabbos's parsha
        """
        # if today is not Shabbos, then there is no normal parsha reading. If
        # commented our will return LAST week's parsha for a non shabbos
        if self.dayofweek != 7:
            return None
        # kvia = whether a Jewish year is short/regular/long (0/1/2)
        # rosh_hashana = Rosh Hashana of this Jewish year
        # rh_day= day of week Rosh Hashana was on this year
        # week= current week in Jewish calendar from Rosh Hashana
        kvia = self.get_cheshvan_kislev_kviah()
        rosh_hashana = JewishDate(self.jyear, TISHREI, 1) # set it to Rosh Hashana of this year
        rh_day = rosh_hashana.dayofweek
        # week is the week since the first Shabbos on or after Rosh Hashana
        week = int(((self.dt.toordinal() - rosh_hashana.dt.toordinal()) - (7 - rh_day)) / 7)
        # determine appropriate array
        if self.in_israel:
            array = PARSHA_ARRAY_ISRAEL.get((rh_day, kvia, self.is_jyear_leap()), None)
        else:
            array = PARSHA_ARRAY_DIASPORA.get((rh_day, kvia, self.is_jyear_leap()), None)
        if not array:
            raise ValueError("""Unable to calculate the parsha. No index array matched any of the
                             known types for the date: """ + str(self))
        return array[week]

    def is_rosh_chodesh(self):
        """Return True if the day is Rosh Chodesh. Rosh Hashana will return False"""
        # Rosh Hashana is not rosh chodesh. Elul never has 30 days
        return self.jday == 1 and self.jmonth != TISHREI or self.jday == 30

    def get_day_of_omer(self):
        """Return the int value of the Omer day or -1 if the day is not in the omer"""
        # if Nissan and second day of Pesach and on
        if self.jmonth == NISSAN and self.jday >= 16:
            return self.jday - 15
            # if Iyar
        if self.jmonth == IYAR:
            return self.jday + 15
            # if Sivan and before Shavuos
        if self.jmonth == SIVAN and self.jday < 6:
            return self.jday + 44
        return None

    def get_daf_yomi_bavli(self):
        """Return tuple of Mesechta number and Daf of the days Daf Yomi"""
        #The number of daf per masechta. Since the number of blatt in Shekalim changed on the 8th
        # Daf Yomi cycle beginning on June 24, 1975 from 13 to 22, the actual calculation for
        # blattPerMasechta[4] will later be adjusted based on the cycle.
        blatt_per_masechta = [64, 157, 105, 121, 22, 88, 56, 40, 35, 31, 32, 29, 27, 122, 112,
                              91, 66, 49, 90, 82, 119, 119, 176, 113, 24, 49, 76, 14, 120, 110,
                              142, 61, 34, 34, 28, 22, 4, 10, 4, 73]
        date = self.dt
        cycle_num = 0
        daf_num = 0
        if date < DAF_YOMI_START_DATE:
            # TODO: should we return a null or throw an IllegalArgumentException?
            return None
            # raise IllegalArgumentException(date +
            #    " is prior to organized Daf Yomi Bavli cycles that started on "
            #        + DAF_YOMI_START_DATE)
        if date >= SHEKALIM_CHANGE_DATE:
            cycle_num, daf_num = divmod(date.toordinal() - datetime(1975, 6, 24).toordinal(), 2711)
            cycle_num += 8
        else:
            cycle_num, daf_num = divmod(date.toordinal() - datetime(1923, 9, 11).toordinal(), 2702)
            cycle_num += 1
        total = 0
        masechta = -1
        blatt = 0

        if cycle_num <= 7: # Fix Shekalim for old cycles.
            blatt_per_masechta[4] = 13
        else:
            blatt_per_masechta[4] = 22
        for j in range(0, len(blatt_per_masechta)): # Finally find the daf.
            masechta += 1 #why is this necesar - isnt it the same as j
            total = total + blatt_per_masechta[j] - 1
            if daf_num < total:
                blatt = 1 + blatt_per_masechta[j] - (total - daf_num)
                # Fiddle with the weird ones near the end.
                if masechta == 36:
                    blatt += 21
                elif masechta == 37:
                    blatt += 24
                elif masechta == 38:
                    blatt += 33
                return masechta, blatt
