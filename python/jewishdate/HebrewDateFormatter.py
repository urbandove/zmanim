#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
 * Zmanim Java API
 * Copyright (C) 2011 Eliyahu Hershfeld
 * Copyright (C) September 2002 Avrom Finkelstien
 *
 * This library is free software you can redistribute it and/or modify it under the terms of
 * the GNU Lesser General Public License as published by the Free Software Foundation either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,but WITHOUT ANY WARRANTY
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU Lesser General Public License for more details.
 * You should have received a copy of the GNU Lesser General Public License along with this
 * library if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth
 * Floor, Boston, MA  02110-1301  USA, or connect to:
 * http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
 """

from .JewishDate import JewishDate, JewishCalendar
FORMAT_DELIMITER = '#'
class HebrewDateFormatter(object):
    """The HebrewDateFormatter class formats a JewishDate.
    The class formats Jewish dates in Hebrew or Latin chars, and has various settings.
    Author: Eliyahu Hershfeld 2011
    Version: 0.3
    """
    hebrew = False
    use_long_hebrew_years = False
    use_gersh_gershayim = True
    long_week_format = True

    GERESH = "׳"
    GERSHAYIM = "״"
    transliterated_months = ["Nissan", "Iyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei",
                             "Cheshvan", "Kislev", "Teves", "Shevat", "Adar", "Adar II",
                             "Adar I"]
    hebrew_omer_prefix = "ב"
    transliterated_shabbos = "Shabbos"
    transliterated_holidays = ["Erev Pesach", "Pesach", "Chol Hamoed Pesach", "Pesach Sheni",
                               "Erev Shavuos", "Shavuos", "Seventeenth of Tammuz", "Tishah B'Av",
                               "Tu B'Av", "Erev Rosh Hashana", "Rosh Hashana", "Fast of Gedalyah",
                               "Erev Yom Kippur", "Yom Kippur", "Erev Succos", "Succos",
                               "Chol Hamoed Succos", "Hoshana Rabbah", "Shemini Atzeres",
                               "Simchas Torah", "Erev Chanukah", "Chanukah", "Tenth of Teves",
                               "Tu B'Shvat", "Fast of Esther", "Purim", "Shushan Purim",
                               "Purim Katan", "Rosh Chodesh", "Yom HaShoah", "Yom Hazikaron",
                               "Yom Ha'atzmaut", "Yom Yerushalayim", "Lag BaOmer"]
    hebrew_holidays = ["ערב פסח", "פסח", "חול המועד פסח", "פסח שני", "ערב שבועות", "שבועות",
                       "שבעה עשר בתמוז", "תשעה באב", "ט״ו באב", "ערב ראש השנה", "ראש השנה",
                       "צום גדליה", "ערב יום כיפור", "יום כיפור", "ערב סוכות", "סוכות",
                       "חול המועד סוכות", "הושענא רבה", "שמיני עצרת", "שמחת תורה", "ערב חנוכה",
                       "חנוכה", "עשרה בטבת", "ט״ו בשבט", "תענית אסתר", "פורים", "פורים שושן",
                       "פורים קטן", "ראש חודש", "יום השואה", "יום הזיכרון", "יום העצמאות",
                       "יום ירושלים", 'ל"ג בעומר']
    hebrew_months = ["ניסן", "אייר", "סיון", "תמוז", "אב", "אלול", "תשרי", "חשון",
                     "כסלו", "טבת", "שבט", "אדר", "אדר ב", "אדר א"]
    transliterated_parshios = ["Bereshis", "Noach", "Lech Lecha", "Vayera", "Chayei Sara", "Toldos",
                               "Vayetzei", "Vayishlach", "Vayeshev", "Miketz", "Vayigash",
                               "Vayechi", "Shemos", "Vaera", "Bo", "Beshalach", "Yisro",
                               "Mishpatim", "Terumah", "Tetzaveh", "Ki Sisa", "Vayakhel", "Pekudei",
                               "Vayikra", "Tzav", "Shmini", "Tazria", "Metzora", "Achrei Mos",
                               "Kedoshim", "Emor", "Behar", "Bechukosai", "Bamidbar", "Nasso",
                               "Beha'aloscha", "Sh'lach", "Korach", "Chukas", "Balak", "Pinchas",
                               "Matos", "Masei", "Devarim", "Vaeschanan", "Eikev", "Re'eh",
                               "Shoftim", "Ki Seitzei", "Ki Savo", "Nitzavim", "Vayeilech",
                               "Ha'Azinu", "Vayakhel Pekudei", "Tazria Metzora",
                               "Achrei Mos Kedoshim", "Behar Bechukosai", "Chukas Balak",
                               "Matos Masei", "Nitzavim Vayeilech"]
    hebrew_parshiyos = ["בראשית", "נח", "לך לך", "וירא", "חיי שרה", "תולדות", "ויצא", "וישלח",
                        "וישב", "מקץ", "ויגש", "ויחי", "שמות", "וארא", "בא", "בשלח", "יתרו",
                        "משפטים", "תרומה", "תצוה", "כי תשא", "ויקהל", "פקודי", "ויקרא", "צו",
                        "שמיני", "תזריע", "מצרע", "אחרי מות", "קדושים", "אמור", "בהר", "בחקתי",
                        "במדבר", "נשא", "בהעלתך", "שלח לך", "קרח", "חוקת", "בלק", "פינחס",
                        "מטות", "מסעי", "דברים", "ואתחנן", "עקב", "ראה", "שופטים", "כי תצא",
                        "כי תבוא", "ניצבים", "וילך", "האזינו", "ויקהל פקודי", "תזריע מצרע",
                        "אחרי מות קדושים", "בהר בחקתי", "חוקת בלק", "מטות מסעי", "ניצבים וילך"]
    hebrewDaysOfWeek = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "ששי", "שבת"]
    masechtos_bavli_transliterated = ["Berachos", "Shabbos", "Eruvin", "Pesachim", "Shekalim",
                                      "Yoma", "Sukkah", "Beitzah", "Rosh Hashana", "Taanis",
                                      "Megillah", "Moed Katan", "Chagigah", "Yevamos", "Kesubos",
                                      "Nedarim", "Nazir", "Sotah", "Gitin", "Kiddushin",
                                      "Bava Kamma", "Bava Metzia", "Bava Basra", "Sanhedrin",
                                      "Makkos", "Shevuos", "Avodah Zarah", "Horiyos", "Zevachim",
                                      "Menachos", "Chullin", "Bechoros", "Arachin", "Temurah",
                                      "Kerisos", "Meilah", "Kinnim", "Tamid", "Midos", "Niddah"]
    masechtos_bavli = ["ברכות", "שבת", "עירובין", "פסחים", "שקלים", "יומא", "סוכה", "ביצה",
                       "ראש השנה", "תענית", "מגילה", "מועד קטן", "חגיגה", "יבמות", "כתובות",
                       "נדרים", "נזיר", "סוטה", "גיטין", "קידושין", "בבא קמא", "בבא מציאה",
                       "בבא בתרא", "סנהדרין", "מכות", "שבועות", "עבודה זרה", "הוריות", "זבחים",
                       "מנחות", "חולין", "בכורות", "ערכין", "תמורב", "כריתות", "מעילה", "תמיד",
                       "קנים", "מדות", "נדה"]
    """

    %w	Weekday as a decimal number, where 0 is Sunday and 6 is Saturday.	1
    %d	Day of the month as a zero-padded decimal number.	30
    %j	Day of the year as a zero-padded decimal number.	273
    %-j	Day of the year as a decimal number. (Platform specific)	273
    %U	Week number of the year (Sunday as the first day of the week) as a zero padded decimal number. All days in a new year preceding the first Sunday are considered to be in week 0.	39
    %W	Week number of the year (Monday as the first day of the week) as a decimal number. All days in a new year preceding the first Monday are considered to be in week 0.	39

    """
    #!a = hebrew day name (yom rishon)
    #!A = endlish day name (with shabbos)
    #!b = hebrew month name
    #!B = english jewish month name
    #!c = hebrew day as letter (if they want a geresh they can add it)
    #!d = 0 padded hebrew day (01 or 19)
    #!D = non zero padded hebrew day (1 or 19)
    #!e = hebrew day of month in hebrew with geresh
    #!E = hebrew day of month in hebrew without geresh
    #!m = month number 0 padded
    #!M = month number no zero padding
    #!y = jewish year hebrew without thousands (geresh is on by default - it isnt guaranteed)
    #!Y = jewish year 4 digits (5778)

    #Specific to jewish calendar objects:
    
    #h = hebrew yom tov name
    #H = transliterated yom tov name
    #o = omer as non zero padded number
    #O = omer in hebrew with geresh
    #p = parsha in hebrew
    #P = parsha in english
    #q = Shabbos/Pashars (if not a parsha show shaboos + yom tov name) in hebrew
    #Q = smae as above in english



    def format(self, jewishdate, format_string):
        format_array = format_string.split(FORMAT_DELIMITER)
        result = []
        index = 0
        already_dbl_hash = False
        for i, piece in enumerate(format_array):
            if not piece and index == 0:
                index += 1
            else:
                if not piece and (index == 1):
                    result.append(FORMAT_DELIMITER)
                    already_dbl_hash = True
                elif i > 0:
                    # should a non format letter with a # in front return z or empty string? strftime does %z
                    result.append(getattr(self, piece[0], lambda x: ("" if already_dbl_hash else "#")+piece[0])(jewishdate)+piece[1:])
                    already_dbl_hash = False
                else:#
                    result.append(piece)
                    already_dbl_hash = False
                index = 0
        return jewishdate.dt.strftime(''.join(result))


    def formatYomTov(self, jewishCalendar):
        """Formats the Yom Tov (holiday) in Hebrew or transliterated Latin characters."""
        index = jewishCalendar.get_yom_tov_index()
        if index == JewishCalendar.CHANUKAH:
            dayOfChanukah = jewishCalendar.getDayOfChanukah()
            if self.hebrew:
                return (self.formatHebrewNumber(dayOfChanukah) + " " + self.hebrew_holidays[index])
            else:
                return (self.transliterated_holidays[index] + " " +  str(dayOfChanukah))
        if not index:
            return ""
        else:
            if self.hebrew:
                return self.hebrew_holidays[index]
            else:
                return self.transliterated_holidays[index]

    def __init__(self, hebrew=False):
        self.hebrew = hebrew

    def formatRoshChodesh(self, jewishCalendar):
        """Return string in English or Hebrew eg. "Rosh Chodesh Tammuz"."""
        if not jewishCalendar.isRoshChodesh():
            return ""
        formatted_rosh_chodesh = ""
        month = jewishCalendar.jmonth
        if jewishCalendar.jday == 30:
            if (month < JewishCalendar.ADAR or
                    (month == JewishCalendar.ADAR and jewishCalendar.is_jyear_leap())):
                month += 1
            else: # roll to Nissan
                month = JewishCalendar.NISSAN
        if self.hebrew:
            formatted_rosh_chodesh = self.hebrew_holidays[JewishCalendar.ROSH_CHODESH]
        else:
            formatted_rosh_chodesh = self.transliterated_holidays[JewishCalendar.ROSH_CHODESH]
        formatted_rosh_chodesh += " " + self.format_month(month)
        return formatted_rosh_chodesh


    def a(self, jewishdate):
        return self.hebrewDaysOfWeek[jewishdate.dayofweek - 1]

    def A(self, jewishdate):
        if jewishdate.dayofweek == 7:
            return self.transliterated_shabbos
        else:
            return jewishdate.dt.strftime('%A')

    def c(self, jewishdate):
        return self.formatHebrewNumber(jewishdate.dayofweek)


    


    def formatDayOfWeek(self, jewishdate):
        """Return String of day of week in english or Hebrew."""
        if self.hebrew:
            if self.long_week_format:
                return self.a(jewishdate)
            else:
                return self.c(jewishdate)
        else:
            return self.A(jewishdate)


    def d(self, jewishdate):
        return '{:02d}'.format(jewishdate.jday)

    def D(self, jewishdate):
        return str(jewishdate.jday)

    def m(self, jewishdate):
        return '{:02d}'.format(jewishdate.jmonth)

    def M(self, jewishdate):
        return str(jewishdate.jmonth)


    def e(self, jewishdate):
        current_geresh = self.use_gersh_gershayim
        self.use_gersh_gershayim = True
        value = self.formatHebrewNumber(jewishdate.jday)
        self.use_gersh_gershayim = current_geresh
        return value

    def E(self, jewishdate):
        current_geresh = self.use_gersh_gershayim
        self.use_gersh_gershayim = False
        value = self.formatHebrewNumber(jewishdate.jday)
        self.use_gersh_gershayim = current_geresh
        return value

    def y(self, jewishdate):
        current_long_jyear = self.use_long_hebrew_years
        self.use_long_hebrew_years = False
        value = self.formatHebrewNumber(jewishdate.jyear)
        self.use_long_hebrew_years = current_long_jyear
        return value

    def Y(self, jewishdate):
        return str(jewishdate.jyear)
            

    def format_parsha(self, jewish_calendar):
        """Return a string of the parsha name"""
        index = jewish_calendar.get_parsha_index()
        if index is None:
            return ""
        else:
            if self.hebrew:
                return self.hebrew_parshiyos[index]
            else:
                return self.transliterated_parshios[index]

    def format_date(self, jewish_date):
        """Return string of Jewish Date in format "d m y" in english or Hebrew"""
        if self.hebrew:
            return (self.formatHebrewNumber(jewish_date.jday) + " " + self.format_month(jewish_date)
                    + " " + self.formatHebrewNumber(jewish_date.jyear))
        else:
            return (str(jewish_date.jday) + " " + self.format_month(jewish_date) + ", "
                    + str(jewish_date.jyear))

    

    def b(self, jewishdate):
        if jewishdate.jmonth == JewishDate.ADAR and jewishdate.is_jyear_leap():
            if self.use_gersh_gershayim:
                return self.hebrew_months[13] + self.GERESH
            else:
                return self.hebrew_months[13]
        elif jewishdate.jmonth == JewishDate.ADAR_II and jewishdate.is_jyear_leap(): # return Adar I, not Adar in a leap year
            if self.use_gersh_gershayim:
                return self.hebrew_months[12] + self.GERESH
            else:
                return self.hebrew_months[12]
        else:
            return self.hebrew_months[jewishdate.jmonth - 1]


    def B(self, jewishdate):
        if jewishdate.jmonth == JewishDate.ADAR and jewishdate.is_jyear_leap():
            return self.transliterated_months[13] # return Adar I, not Adar in a leap year
        else:
            return self.transliterated_months[jewishdate.jmonth - 1]


    def format_month(self, jewishdate):
        """Returns a string of the current Hebrew month such as "Tishrei". or "תשרי". """
        if self.hebrew:
            return self.b(jewishdate)
        else:
            return self.B(jewishdate)
            

    def formatOmer(self, jewishCalendar):
        """Return string of day of omer - or Empty string if none"""
        omer = jewishCalendar.getDayOfOmer()
        if not omer:
            return ""
        if self.hebrew:
            return self.formatHebrewNumber(omer) + " " + self.hebrew_omer_prefix + "עומר"
        else:
            if omer == 33: # if lag b'omer
                return "Lag BaOmer"
            else:
                return "Omer " + str(omer)

    def formatMolad(self, chalakim):
        """Return formatted Molad"""
        MINUTE_CHALAKIM = 18
        HOUR_CHALAKIM = 1080
        DAY_CHALAKIM = 24 * HOUR_CHALAKIM
        d, chalakim = divmod(chalakim, DAY_CHALAKIM)  # Days
        h, chalakim = divmod(chalakim, HOUR_CHALAKIM)  # Hours
        if (h >= 6):
            d += 1
        m, chalakim = divmod(chalakim, MINUTE_CHALAKIM)  # minutes
        return "Day: %s, hours: %s, minutes:  %s, chalakim: %s" % (d%7, h, m, chalakim)

    def getFormattedKviah(self, jewishYear):
        """Returns the kviah in the traditional 3 letter Hebrew format where the first
        letter represents the day of week of Rosh Hashana, the second letter represents
        the lengths of Cheshvan and Kislev and the 3rd letter represents the day of
        week of Pesach.
        """
        jewishDate = JewishDate(jewishYear, JewishDate.TISHREI, 1) # set date to Rosh Hashana
        kviah = jewishDate.get_cheshvan_kislev_kviah()
        roshHashanaDayOfweek = jewishDate.dayofweek
        returnValue = self.formatHebrewNumber(roshHashanaDayOfweek)
        if kviah == JewishDate.CHASERIM:
            returnValue += "ח"
        elif kviah == JewishDate.SHELAIMIM:
            returnValue += "ש"
        else:
            returnValue += "כ"
        jewishDate.set_jdate(jewishYear, JewishDate.NISSAN, 15) # set to Pesach of the given year
        pesachDayOfweek = jewishDate.dayofweek
        returnValue += self.formatHebrewNumber(pesachDayOfweek)
        returnValue = returnValue.replace(self.GERESH, "")  # geresh is never used in the kviah format
        # boolean isLeapYear = JewishDate.isJewishLeapYear(jewishYear)
        # for efficiency we can avoid the expensive recalculation of the pesach day of week by adding 1 day to Rosh
        # Hashana for a 353 day year, 2 for a 354 day year, 3 for a 355 or 383 day year, 4 for a 384 day year and 5 for
        # a 385 day year
        return returnValue

    def formatDafYomiBavli(self, daf):
        """Return a formatted Daf Yomi of the Day in English or Hebrew
        takes a tuple rurned by JewishCalendar.getDafYomiBavli()
        """
        if self.hebrew:
            return self.masechtos_bavli[daf[0]] + " " + self.formatHebrewNumber(daf[1])
        else:
            return self.masechtos_bavli_transliterated[daf[0]] + " " + daf[1]

    def formatHebrewNumber(self, number):
        """Returns a Hebrew formatted string of a number. The method can calculate from 0 - 9999"""
        if (number < 0):
            raise ValueError("negative numbers can't be formatted")
        elif (number > 9999):
            raise ValueError("numbers > 9999 can't be formatted")
        ALAFIM = "אלפים"
        EFES = "אפס"
        jHundreds = [ "", "ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק"]
        jTens =[ "", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ" ]
        jTenEnds =[ "", "י", "ך", "ל", "ם", "ן", "ס", "ע", "ף", "ץ" ]
        jOnes = [ "", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט" ]

        if number == 0: # do we realy need this? Should it be applicable to a date?
            return EFES
    
        thousands, shortNumber = divmod(number, 1000) # seperate thousands
        # next check for all possible single Hebrew digit years
        singleDigitNumber = (shortNumber < 11
                or (shortNumber < 100 and shortNumber % 10 == 0)
                or (shortNumber <= 400 and shortNumber % 100 == 0))
        sb = []
        # append thousands to String
        if not shortNumber: # in year is 5000, 4000 etc
            sb.append(jOnes[thousands])
            if self.use_gersh_gershayim:
                sb.append(GERESH)
            sb.append(" ")
            sb.append(ALAFIM) # add # of thousands plus word thousand (overide alafim boolean)
            return "".join(sb)
        elif (self.use_long_hebrew_years and thousands): # if alafim boolean display thousands
            sb.append(jOnes[thousands])
            if self.use_gersh_gershayim:
                sb.append(GERESH) # append thousands quote
            sb.append(" ")
        hundreds, number = divmod(shortNumber, 100)
        sb.append(jHundreds[hundreds]) # add hundreds to String
        if (number == 15): # special case 15
            sb.append("ט")
            sb.append("ו")
        elif (number == 16): # special case 16
            sb.append("ט")
            sb.append("ז")
        else:
            tens, ones = divmod(number, 10)
            if not ones: # if evenly divisable by 10
                if not singleDigitNumber:
                    sb.append(jTenEnds[tens]) # end letters so years like 5750 will end with an end nun
                else:
                    sb.append(jTens[tens]) # standard letters so years like 5050 will end with a regular nun
            else:
                sb.append(jTens[tens])
                sb.append(jOnes[ones])

        if self.use_gersh_gershayim:
            if singleDigitNumber:
                sb.append(self.GERESH)  # append single quote
            else: # append double quote before last digit
                a = sb[len(sb)-1]
                sb[len(sb)-1] = self.GERSHAYIM
                sb.append(a)
    
        return "".join(sb)
