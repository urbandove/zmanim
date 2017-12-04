'use strict';
/*Zmanim Java API
 * Copyright (C) 2011 Eliyahu Hershfeld
 * Copyright (C) September 2002 Avrom Finkelstien 
 *
 * This library is free software you can redistribute it and/or modify it under the terms of the GNU Lesser General
 * Public License as published by the Free Software Foundation either version 2.1 of the License, or (at your option)
 * any later version.
 *
 * This library is distributed in the hope that it will be useful,but WITHOUT ANY WARRANTY without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 * details.
 * You should have received a copy of the GNU Lesser General Public License along with this library if not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA,
 * or connect to: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html*/
//from JewishDate import JewishDate, JewishCalendar

class HebrewDateFormatter{
    /*The HebrewDateFormatter class formats a JewishDate.
    The class formats Jewish dates in Hebrew or Latin chars, and has various settings.
    Author: Eliyahu Hershfeld 2011
    Version: 0.3*/
    constructor(){
        this.hebrew = false
        this.use_long_hebrew_years = false
        this.use_gersh_gershayim = true
        this.long_week_format = true
        this.GERESH = "׳"
        this.GERSHAYIM = "״"
        this.transliterated_months = ["Nissan", "Iyar", "Sivan", "Tammuz", "Av", "Elul", "Tishrei", "Cheshvan",
                "Kislev", "Teves", "Shevat", "Adar", "Adar II", "Adar I"]
        this.hebrew_omer_prefix = "ב"
        this.day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Shabbos"]
        this.transliterated_holidays = ["Erev Pesach", "Pesach", "Chol Hamoed Pesach", "Pesach Sheni",
                "Erev Shavuos", "Shavuos", "Seventeenth of Tammuz", "Tishah B'Av", "Tu B'Av", "Erev Rosh Hashana",
                "Rosh Hashana", "Fast of Gedalyah", "Erev Yom Kippur", "Yom Kippur", "Erev Succos", "Succos",
                "Chol Hamoed Succos", "Hoshana Rabbah", "Shemini Atzeres", "Simchas Torah", "Erev Chanukah", "Chanukah",
                "Tenth of Teves", "Tu B'Shvat", "Fast of Esther", "Purim", "Shushan Purim", "Purim Katan", "Rosh Chodesh",
                "Yom HaShoah", "Yom Hazikaron", "Yom Ha'atzmaut", "Yom Yerushalayim", "Lag BaOmer" ]
        this.hebrew_holidays = [ "ערב פסח", "פסח", "חול המועד פסח", "פסח שני", "ערב שבועות", "שבועות",
                "שבעה עשר בתמוז", "תשעה באב", "ט״ו באב", "ערב ראש השנה", "ראש השנה", "צום גדליה",
                "ערב יום כיפור", "יום כיפור", "ערב סוכות", "סוכות", "חול המועד סוכות", "הושענא רבה", "שמיני עצרת",
                "שמחת תורה", "ערב חנוכה", "חנוכה", "עשרה בטבת", "ט״ו בשבט", "תענית אסתר", "פורים", "פורים שושן",
                "פורים קטן", "ראש חודש", "יום השואה", "יום הזיכרון", "יום העצמאות", "יום ירושלים", 'ל"ג בעומר']
        this.hebrew_months = [ "ניסן", "אייר","סיוון", "תמוז", "אב", "אלול","תשרי", "חשוון", "כסלו","טבת", "שבט", "אדר", "אדר ב","אדר א" ]
        this.transliterated_parshios = ["Bereshis", "Noach", "Lech Lecha", "Vayera", "Chayei Sara", "Toldos",
            "Vayetzei", "Vayishlach", "Vayeshev", "Miketz", "Vayigash", "Vayechi", "Shemos", "Vaera", "Bo",
            "Beshalach", "Yisro", "Mishpatim", "Terumah", "Tetzaveh", "Ki Sisa", "Vayakhel", "Pekudei", "Vayikra",
            "Tzav", "Shmini", "Tazria", "Metzora", "Achrei Mos", "Kedoshim", "Emor", "Behar", "Bechukosai", "Bamidbar",
            "Nasso", "Beha'aloscha", "Sh'lach", "Korach", "Chukas", "Balak", "Pinchas", "Matos", "Masei", "Devarim",
            "Vaeschanan", "Eikev", "Re'eh", "Shoftim", "Ki Seitzei", "Ki Savo", "Nitzavim", "Vayeilech", "Ha'Azinu",
            "Vayakhel Pekudei", "Tazria Metzora", "Achrei Mos Kedoshim", "Behar Bechukosai", "Chukas Balak",
            "Matos Masei", "Nitzavim Vayeilech"]
        this.hebrew_parshiyos =[ "בראשית", "נח", "לך לך", "וירא", "חיי שרה", "תולדות", "ויצא", "וישלח", "וישב", "מקץ", "ויגש", "ויחי",
            "שמות", "וארא", "בא", "בשלח", "יתרו", "משפטים", "תרומה", "תצוה", "כי תשא", "ויקהל", "פקודי",
            "ויקרא", "צו", "שמיני", "תזריע", "מצרע", "אחרי מות", "קדושים", "אמור", "בהר", "בחקתי",
            "במדבר", "נשא", "בהעלתך", "שלח לך", "קרח", "חוקת", "בלק", "פינחס", "מטות", "מסעי",
            "דברים", "ואתחנן", "עקב", "ראה", "שופטים", "כי תצא", "כי תבוא", "ניצבים", "וילך", "האזינו",

            "ויקהל פקודי", "תזריע מצרע", "אחרי מות קדושים", "בהר בחקתי", "חוקת בלק", "מטות מסעי", "ניצבים וילך" ]
        this.hebrewDaysOfWeek =[ "ראשון", "שני", "שלישי", "רביעי", "חמישי", "ששי", "שבת" ]
        this.masechtos_bavli_transliterated = [ "Berachos", "Shabbos", "Eruvin", "Pesachim", "Shekalim",
                "Yoma", "Sukkah", "Beitzah", "Rosh Hashana", "Taanis", "Megillah", "Moed Katan", "Chagigah", "Yevamos",
                "Kesubos", "Nedarim", "Nazir", "Sotah", "Gitin", "Kiddushin", "Bava Kamma", "Bava Metzia", "Bava Basra",
                "Sanhedrin", "Makkos", "Shevuos", "Avodah Zarah", "Horiyos", "Zevachim", "Menachos", "Chullin", "Bechoros",
                "Arachin", "Temurah", "Kerisos", "Meilah", "Kinnim", "Tamid", "Midos", "Niddah" ]
        this.masechtos_bavli =[ "ברכות", "שבת", "עירובין", "פסחים", "שקלים", "יומא", "סוכה", "ביצה",
                                            "ראש השנה", "תענית", "מגילה", "מועד קטן", "חגיגה", "יבמות", "כתובות", "נדרים",
                                            "נזיר", "סוטה", "גיטין", "קידושין", "בבא קמא", "בבא מציאה", "בבא בתרא", "סנהדרין", "מכות",
                                            "שבועות", "עבודה זרה", "הוריות", "זבחים", "מנחות", "חולין", "בכורות", "ערכין",
                                            "תמורב", "כריתות", "מעילה", "תמיד", "קנים", "מדות", "נדה"]
    }
    

    


    formatYomTov(jewishCalendar){
        //Formats the Yom Tov (holiday) in Hebrew or transliterated Latin characters.
        let index = jewishCalendar.getYomTovIndex()
        if (index == JewishCalendar.CHANUKAH){
            dayOfChanukah = jewishCalendar.getDayOfChanukah()
            return this.hebrew ? (this.formatHebrewNumber(dayOfChanukah) + " " + this.hebrew_holidays[index]) : (this.transliterated_holidays[index] + " " +  dayOfChanukah)
        }
        if (!index){
            return ""
        } else{
            return this.hebrew ? this.hebrew_holidays[index] : this.transliterated_holidays[index]
        }
    }

    formatRoshChodesh(jewishCalendar){
        //Return string in English or Hebrew eg. "Rosh Chodesh Tammuz".
        if (!jewishCalendar.isRoshChodesh()){
            return ""
        }
        let formattedRoshChodesh = ""
        let month = jewishCalendar.jmonth
        if (jewishCalendar.jday == 30){
            if (month < JewishCalendar.ADAR || (month == JewishCalendar.ADAR && jewishCalendar.isJewishLeapYear())){
                month +=1
            } else { // roll to Nissan
                month = JewishCalendar.NISSAN
            }
        }
        formattedRoshChodesh = this.hebrew ? hebrew_holidays[JewishCalendar.ROSH_CHODESH] : transliterated_holidays[JewishCalendar.ROSH_CHODESH]
        formattedRoshChodesh += " " + this.formatMonth(month)
        return formattedRoshChodesh
    }

    formatDayOfWeek(jewishDate){
        //Return String of day of week in english or Hebrew.
        if (this.hebrew){
            return this.long_week_format ? hebrewDaysOfWeek[jewishDate.dayofweek - 1] : this.formatHebrewNumber(jewishDate.dayofweek)
        } else{
            return this.day_names[jewishDate.dayofweek - 1]
        }
    }

    formatParsha(jewishCalendar){
        //Return a string of the parsha name
        let index = jewishCalendar.getParshaIndex()
        if (!index){
            return ""
        } else{ 
            return this.hebrew ? this.hebrew_parshiyos[index] : this.transliterated_parshios[index]
        }
    }

    format_date(jewishDate){
        //Return string of Jewish Date in format "d m y" in english or Hebrew
        if (this.hebrew){
            return (this.formatHebrewNumber(jewishDate.jday) + " " + this.formatMonth(jewishDate) + " "
                    + this.formatHebrewNumber(jewishDate.jyear))
        } else {
            return jewishDate.jday + " " + this.formatMonth(jewishDate) + ", " + jewishDate.jyear
        }
    }

    formatMonth(jd){
        //Returns a string of the current Hebrew month such as "Tishrei". or "תשרי".
        let month = ((typeof(jd) === 'number') ? jd : jd.jmonth)
        if (this.hebrew){
            if (jd.isJewishLeapYear() && month === 12){
                return this.use_gersh_gershayim ? this.hebrew_months[13] + this.GERESH : this.hebrew_months[13]
            } else if (jd.isJewishLeapYear() && month === 13){ // return Adar I, not Adar in a leap year
                return this.use_gersh_gershayim ? this.hebrew_months[12] + this.GERESH : this.hebrew_months[12]
            } else {
                return this.hebrew_months[month - 1]
            }
        } else {
            return (JewishDate.isJewishLeapYear(jd.jyear) && month == 12) ? this.transliterated_months[13] : this.transliterated_months[month - 1]
        }
    }

    formatOmer(jewishCalendar){
        //Return string of day of omer - or Empty string if none"""
        let omer = jewishCalendar.getDayOfOmer()
        if (!omer){
            return ""
        }
        if (this.hebrew){
            return this.formatHebrewNumber(omer) + " " + this.hebrew_omer_prefix + "עומר"
        } else{
            return omer == 33 ? "Lag BaOmer" : "Omer " + omer
        }
                
    }

    /*formatMolad(chalakim){
        //Return formatted Molad
        let MINUTE_CHALAKIM = 18
        let HOUR_CHALAKIM = 1080
        let DAY_CHALAKIM = 24 * HOUR_CHALAKIM
        d, chalakim = divmod(chalakim, DAY_CHALAKIM)  // Days
        h, chalakim = divmod(chalakim, HOUR_CHALAKIM)  // Hours
        if (h >= 6):
            d += 1
        m, chalakim = divmod(chalakim, MINUTE_CHALAKIM)  // minutes
        return "Day: %s, hours: %s, minutes:  %s, chalakim: %s" % (d%7, h, m, chalakim)
    }*/

    getFormattedKviah(jewishYear){
        /*Returns the kviah in the traditional 3 letter Hebrew format where the first
        letter represents the day of week of Rosh Hashana, the second letter represents
        the lengths of Cheshvan and Kislev and the 3rd letter represents the day of
        week of Pesach.*/
        let jewishDate = JewishDate(jewishYear, 7, 1) // set date to Rosh Hashana
        let kviah = jewishDate.getCheshvanKislevKviah()
        let roshHashanaDayOfweek = jewishDate.dayofweek
        let returnValue = this.formatHebrewNumber(roshHashanaDayOfweek)
        if (kviah == JewishDate.CHASERIM){
            returnValue += "ח"
        } else if (kviah == JewishDate.SHELAIMIM){
            returnValue += "ש"
        } else {
            returnValue += "כ"
        }
        jewishDate.setJewishDate(jewishYear, JewishDate.NISSAN, 15) // set to Pesach of the given year
        let pesachDayOfweek = jewishDate.dayofweek
        returnValue += this.formatHebrewNumber(pesachDayOfweek)
        returnValue = returnValue.replace(this.GERESH, "")  // geresh is never used in the kviah format
        // boolean isLeapYear = JewishDate.isJewishLeapYear(jewishYear)
        // for efficiency we can avoid the expensive recalculation of the pesach day of week by adding 1 day to Rosh
        // Hashana for a 353 day year, 2 for a 354 day year, 3 for a 355 or 383 day year, 4 for a 384 day year and 5 for
        // a 385 day year
        return returnValue
    }

    formatDafYomiBavli(daf){
        /*Return a formatted Daf Yomi of the Day in English or Hebrew
        takes a tuple rurned by JewishCalendar.getDafYomiBavli()*/
        return this.hebrew ?  this.masechtos_bavli[daf[0]] + " " + this.formatHebrewNumber(daf[1]) : this.masechtos_bavli_transliterated[daf[0]] + " " + daf[1]
    }

    formatHebrewNumber(number){
        //Returns a Hebrew formatted string of a number. The method can calculate from 0 - 9999
        if (number < 0){
            throw new ValueError("negative numbers can't be formatted")
        } else if (number > 9999){
            throw new ValueError("numbers > 9999 can't be formatted")
        }
        let ALAFIM = "אלפים"
        let EFES = "אפס"
        let jHundreds = [ "", "ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק"]
        let jTens =[ "", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ" ]
        let jTenEnds =[ "", "י", "ך", "ל", "ם", "ן", "ס", "ע", "ף", "ץ" ]
        let tavTaz = [ "טו", "טז" ]
        let jOnes = [ "", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט" ]

        if (number == 0){ // do we realy need this? Should it be applicable to a date?
            return EFES
        }
    
        let [thousands, shortNumber] = divmod(number, 1000) // seperate thousands
        // next check for all possible single Hebrew digit years
        let singleDigitNumber = (shortNumber < 11
                || (shortNumber < 100 && shortNumber % 10 == 0)
                || (shortNumber <= 400 && shortNumber % 100 == 0))
        let sb = []
        // append thousands to String
        if (!shortNumber){ // in year is 5000, 4000 etc
            sb.push(jOnes[thousands])
            if (this.use_gersh_gershayim){
                sb.push(GERESH)
            }
            sb.push(" ")
            sb.push(ALAFIM) // add // of thousands plus word thousand (overide alafim boolean)
            return "".join(sb)
        } else if (this.use_long_hebrew_years && thousands){ // if alafim boolean display thousands
            sb.push(jOnes[thousands])
            if (this.use_gersh_gershayim){
                sb.push(GERESH) // append thousands quote
            }
            sb.push(" ")
        }
        let hundreds = 0
        [hundreds, number] = divmod(shortNumber, 100)
        sb.push(jHundreds[hundreds]) // add hundreds to String
        if (number == 15){ // special case 15
            sb.push(tavTaz[0])
        } else if (number == 16){ // special case 16
            sb.push(tavTaz[1])
        } else {
            let [tens, ones] = divmod(number, 10)
            if (!ones){ // if evenly divisable by 10
                if (!singleDigitNumber){
                    sb.push(jTenEnds[tens]) // end letters so years like 5750 will end with an end nun
                } else {
                    sb.push(jTens[tens]) // standard letters so years like 5050 will end with a regular nun
                }
            } else {
                sb.push(jTens[tens])
                sb.push(jOnes[ones])
            }
        }
        if (this.use_gersh_gershayim){
            if (singleDigitNumber){
                sb.push(this.GERESH)  // append single quote
            } else { // append double quote before last digit
                let a = sb[len(sb)-1]
                sb[len(sb)-1] = this.GERSHAYIM
                sb.push(a)
            }
        }
        return "".join(sb)
    }
}
