const _DAYS_IN_MONTH = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
const NISSAN = 1
const IYAR = 2
const SIVAN = 3
const TAMUZ = 4
const AV = 5
const ELUL = 6
const TISHREI = 7
const CHESHVAN = 8
const KISLEV = 9
const TEVES = 10
const SHEVAT = 11
const ADAR = 12
const ADAR_II = 13
const JEWISH_EPOCH = -1373429  // Jewish Epoch. Day 1 is Jan 1, 0001 Gregorian. From Calendrical Calculations
const CHALAKIM_PER_MINUTE = 18
const CHALAKIM_PER_HOUR = 1080
const CHALAKIM_PER_DAY = 25920 // 24 * 1080
const CHALAKIM_PER_MONTH = 765433 // (29 * 24 + 12) * 1080 + 793
const CHALAKIM_MOLAD_TOHU = 31524  // Chalakim from the beginning of Sunday till molad BaHaRaD.
const CHASERIM = 0  // Cheshvan and Kislev both 29 days
const KESIDRAN = 1  // Cheshvan 29 days and Kislev 30 days
const SHELAIMIM = 2  // Cheshvan and Kislev both 30 days
function divmod(x,y){
    return [Math.floor(x/y), x % y];
}

function ValueError(message) {
   this.message = message;
   this.name = "Value Error";
}

Date.prototype.toordinal = function() {
    return Math.floor((this / 86400000) - (this.getTimezoneOffset()/1440) + 719163);
}

function absDateToDate(absDate) {
    (-719162 + absDate) * 86400000
    let a = new Date()
    return new Date(((-719163 + absDate) * 86400000) + (a.getTimezoneOffset() * 60000))
}


class JewishDate{
    /*Creates a Jewish date
    Arguments:
    year -- can be a datetime object - then all other arguments are disregarded
    year -- the Jewish year. The year can't be negative
    month -- the Jewish month. Nissan = 1 Adar II = 13
    day -- the Jewish day of month*/

    getLastDayOfGregorianMonth(month, year){
        //Returns the number of days in a given month in a given month and year.
        year = year || this.date.getFullYear()
        if (month == 2 && year % 4 == 0 && (year % 100 != 0 || year % 400 === 0)){
            return 29;
        }
        return _DAYS_IN_MONTH[month];
    }

    fromordinal(absDate){
        //Computes the Gregorian date from the absolute date. ND+ER
        this.setDate(absDateToDate(absDate))
    }

    getJulian(){
        //Returns the absolute date (days since January 1, 0001 on the Gregorian calendar).
        return this.date.getJulian()
    }

    static getCheshvanKislevKviah(year){
        //Returns the Cheshvan and Kislev kviah (whether a Jewish year is short, regular or long).
        //Returns 0 for Chaseirim, 1 for Kesidron, and 2 for Shleimim
        let [cheshvan, kislev] = JewishDate.getDaysCheshvanKislev(year);
        let total = cheshvan + kislev;
        if (total === 60){
            return SHELAIMIM
        } else if (total === 58){
            return CHASERIM
        } else {
            return KESIDRAN
        }
    }
            
    static getJewishCalendarElapsedDays(year){
        /*Returns the number of days elapsed from the Sunday prior to the start of the Jewish calendar to the mean
        conjunction of Tishri of the Jewish year.*/
        let chalakimSince = JewishDate.getChalakimSinceMoladTohu(year, TISHREI)
        let [moladDay, moladParts] = divmod(chalakimSince, CHALAKIM_PER_DAY)
        // delay Rosh Hashana for the 4 dechiyos
        return JewishDate.addDechiyos(year, moladDay, moladParts)
    }

    static addDechiyos(year, moladDay, moladParts){
        let roshHashanaDay = moladDay // if no dechiyos
        // delay Rosh Hashana for the dechiyos of the Molad - new moon 1 - Molad Zaken, 2- GaTRaD 3- BeTuTaKFoT
        if (moladParts >= 19440){ // Dechiya of Molad Zaken - molad is >= midday (18 hours * 1080 chalakim)
            roshHashanaDay += 1 // Then postpone Rosh HaShanah one day
        } else {
            let a = moladDay % 7
            if (((a == 2) // start Dechiya of GaTRaD - Ga = is a Tuesday
                && (moladParts >= 9924) // TRaD = 9 hours, 204 parts or later (9 * 1080 + 204)
                && (!JewishDate.isJewishLeapYear(year))) // of a non-leap year - end Dechiya of GaTRaD
            || ((a == 1) // start Dechiya of BeTuTaKFoT - Be = is on a Monday
                && (moladParts >= 16789) // TRaD = 15 hours, 589 parts or later (15 * 1080 + 589)
                && (JewishDate.isJewishLeapYear(year - 1)))){ // in a year following a leap year - end Dechiya of BeTuTaKFoT
                    roshHashanaDay += 1 // Then postpone Rosh HaShanah one day
                }
        }
        // start 4th Dechiya - Lo ADU Rosh - Rosh Hashana can't occur on A- sunday, D- Wednesday, U - Friday
        let a = roshHashanaDay % 7;
        if (a === 0 || a === 3 || a === 5){ // If RH would occur on Sunday,Wednesday or Friday - end 4th Dechiya - Lo ADU Rosh
            roshHashanaDay += 1 // Then postpone it one (more) day
        }
        return roshHashanaDay
    }

    static getChalakimSinceMoladTohu(year, month){
        /*Returns the number of chalakim (parts - 1080 to the hour) from the original hypothetical Molad Tohu to the year
        and month passed in.*/
        
        //Jewish lunar month = 29 days, 12 hours and 793 chalakim
        //chalakim since Molad Tohu BeHaRaD - 1 day, 5 hours and 204 chalakim
        let [metonic_cycles, year_in_cycle] = divmod(year - 1,19)
        let months = (metonic_cycles * 235 // Months in complete 19 year lunar (Metonic) cycles so far
                + year_in_cycle * 12 // Regular months in this cycle
                + Math.floor((7 * year_in_cycle + 1) / 19) // Leap months this cycle
                + JewishDate.getJewishMonthOfYear(year, month) - 1)  // add elapsed months till the start of the molad of the month
        // return chalakim prior to BeHaRaD + number of chalakim since
        return CHALAKIM_MOLAD_TOHU + (CHALAKIM_PER_MONTH * months)
    }
        
    static getDaysSinceStartOfJewishYear(year, month, dayOfMonth){
        //returns the number of days from Rosh Hashana of the date passed in, till the full date passed in.//
        let elapsedDays = dayOfMonth
        // Before Tishrei (from Nissan to Tishrei), add days in prior months
        if (month < TISHREI){
            // this year before and after Nisan.
            for (let m = TISHREI; m < JewishDate.getLastMonthOfJewishYear(year)+1; m++){
                elapsedDays += JewishDate.getDaysInJewishMonth(m, year)
            }
            for (let m = NISSAN; m < month; m++){
                elapsedDays += JewishDate.getDaysInJewishMonth(m, year)
            }
        } else { // Add days in prior months this year
            for (let m = TISHREI; m < month; m++){
                elapsedDays += JewishDate.getDaysInJewishMonth(m, year)
            }
        }
        return elapsedDays;
    }
        
    static jewishDateToAbsDate(year, month, day){
        /*Returns the absolute date of Jewish date. ND+ER
        Arguments:
        year -- Jewish year. The year can't be negative
        month -- Nissan =1 and Adar II = 13
        day -- day of month*/
        let elapsed = JewishDate.getDaysSinceStartOfJewishYear(year, month, day)
        // add elapsed days this year + Days in prior years + Days elapsed before absolute year 1
        return parseInt(elapsed + JewishDate.getJewishCalendarElapsedDays(year) + JEWISH_EPOCH)
    }
        
    static getLastMonthOfJewishYear(year){
        //Return the last month of a given Jewish year. This will be 12 but 13 on leap year
        return JewishDate.isJewishLeapYear(year) ? ADAR_II : ADAR
    }
        
    static getJewishMonthOfYear(year, month){
        /*Converts the Nissan based months used by this class to numeric month starting from Tishrei.
        This is required for Molad claculations.*/
        let isLeapYear = JewishDate.isJewishLeapYear(year);
        return (month + (isLeapYear ? 6 : 5)) % (isLeapYear ? 13 : 12) + 1;
    }

    static getDaysInJewishYear(year){
        //Returns the number of days for a given Jewish year. ND+ER
        return JewishDate.getJewishCalendarElapsedDays(year + 1) - JewishDate.getJewishCalendarElapsedDays(year)
    }

    static isJewishLeapYear(year){
        //Return True if the year is a Jewish leap year. Years 3, 6, 8, 11, 14, 17 and 19 in the 19 year cycle are leap years.
        return ((7 * year) + 1) % 19 < 7
    }
        
    static isCheshvanLong(year){
        //Returns if Cheshvan is long in a given Jewish year.
        return JewishDate.getDaysInJewishYear(year) % 10 == 5
    }

    static isKislevShort(year){
        //Returns if Kislev is short (29 days VS 30 days) in a given Jewish year.//
        return JewishDate.getDaysInJewishYear(year) % 10 == 3
    }
        
    static getDaysCheshvanKislev(year){
        //Returns a tuple containing (days_in_cheshvan, days_in_kislev) for given year//
        let days = JewishDate.getDaysInJewishYear(year),
            cheshvandays = 29,
            kislevdays = 30
        if (days % 10 == 5){
            cheshvandays = 30
        }
        if (days % 10 == 3){
            kislevdays = 29
        }
        return [cheshvandays, kislevdays]
    }

    static getDaysInJewishMonth(month, year){
        //Returns the number of days of a Jewish month for a given month and year.//
        if (month == IYAR || month == TAMUZ
            || month == ELUL || month == TEVES
            || month == ADAR_II){
            return 29
        }
        if ((month == CHESHVAN) && (!JewishDate.isCheshvanLong(year)) ||
            ((month == KISLEV) && JewishDate.isKislevShort(year)) ||
            ((month == ADAR) && (!JewishDate.isJewishLeapYear(year)))){
            return 29
        }
        return 30
    }

    static datetimeToJewishDate(date){
        //Computes the Jewish date from the absolute date. ND+ER//
        let absDate = date.toordinal()
        // Start with approximation
        let jyear = date.getFullYear() + 3760
        // Search forward for year from the approximation
        while (absDate >= JewishDate.jewishDateToAbsDate(jyear + 1, TISHREI, 1)){
            jyear += 1
        }
        let isLeapYear = JewishDate.isJewishLeapYear(jyear)
        //start with tishrei
        let jmonth = TISHREI
        let daysbeyond0ofjmonth = absDate - JewishDate.jewishDateToAbsDate(jyear, jmonth, 1)
        let daysinjmonth = JewishDate.getDaysInJewishMonth(jmonth, jyear)
        //go forward month by month
        while (daysbeyond0ofjmonth >= daysinjmonth){
            jmonth += 1
            if (jmonth > 12){
                if ((!isLeapYear) || jmonth === 14){
                    jmonth = 1
                }
            }
            daysbeyond0ofjmonth -= daysinjmonth
            if (jmonth === CHESHVAN){
                let [cheshvandays, kislevdays] = JewishDate.getDaysCheshvanKislev(jyear)
                if (daysbeyond0ofjmonth >= cheshvandays){
                    jmonth += 1
                    daysbeyond0ofjmonth -= cheshvandays
                }
                if (daysbeyond0ofjmonth >= kislevdays){
                    jmonth += 1
                    daysbeyond0ofjmonth -= kislevdays
                }
            }
            daysinjmonth = JewishDate.getDaysInJewishMonth(jmonth, jyear)
        }
        let jday = daysbeyond0ofjmonth + 1
        return [jyear, jmonth, jday]
    }
        
    static validateJewishDate(year, month, day, hours, minutes, chalakim){
        /*Validates the components of a Jewish date for validity. It will throw a ValueError if the
        Jewish date is earlier than 18 Teves, 3761 (1/1/1 Gregorian), a month < 1 or > 12 (or 13 on a leap year),
        the day of month is < 1 or > 30, an hour < 0 or > 23, a minute < 0 > 59 or chalakim < 0 > 17. For a larger
        number of chalakim such as 793 (TaShTzaG) break the chalakim into minutes (18 chalakim per minutes, so it
        would be 44 minutes and 1 chelek in the case of 793/TaShTzaG).

        Arguments:
        year -- jewish year
        month -- jewish month
        day -- jewish day of month
        hours -- of molad - between 0 and 23
        minutes -- of molad - between 0 and 59
        chalakim -- of molad - between 0 and 17*/
        hours = hours || 0
        minutes = minutes || 0
        chalakim = chalakim || 0
        if (month < NISSAN || month > JewishDate.getLastMonthOfJewishYear(year)){
            throw new ValueError("The Jewish month has to be between 1 and 12 (or 13 on a leap year). %s is invalid for the year %s." % (month, year))
        }
        if (day < 1 || day > 30){
            throw new ValueError("The Jewish day of month can't be < 1 or > 30.  %s is invalid." % (day))
        }
        if (day >= 29){
            if (day > JewishDate.getDaysInJewishMonth(month,year)){
                throw new ValueError("Day is out of range for month")
            }
        }

        // reject dates prior to 18 Teves, 3761 (1/1/1 AD). This restriction can be relaxed if the date coding is
        // changed/corrected
        if ((year < 3761) || (year === 3761 && 6 < month < TEVES)
                || (year == 3761 && month === TEVES && day < 18)){
            throw new ValueError("A Jewish date earlier than 18 Teves, 3761 (1/1/1 Gregorian) can't be set. %s, %s, %s  is invalid." % (year, month, day))
        }


        if (hours < 0 || hours > 23){
            throw new ValueError("Hours < 0 > 23 can't be set. %s is invalid." % (hours))
        }
        if (minutes < 0 || minutes > 59){
            throw new ValueError("Minutes < 0 > 59 can't be set. %s is invalid." % (minutes))
        }
        if (chalakim < 0 || chalakim > 17){
            throw new ValueError(`Chalakim/parts < 0 > 17 can't be set. %s is invalid. For larger numbers 
                            such as 793 (TaShTzaG) break the chalakim into minutes (18 chalakim per minutes, 
                            so it would be 44 minutes and 1 chelek in the case of 793 (TaShTzaG)` % (chalakim))
        }
        return [year, month, day, hours, minutes, chalakim]
    }

    getMolad(){
        /*Return the molad for a given year and month (between this month and preceding month). Returns a JewishDate set to the date of the molad
        with the molad_hours, molad_minutes and molad_chalakim set. In the current implementation, it
        sets the molad time based on a midnight date rollover. This means that Rosh Chodesh Adar II, 5771
        with a molad of 7 chalakim past midnight on Shabbos 29 Adar I / March 5, 2011 12:00 AM and 7 chalakim,
        will have the following values: hours: 0, minutes: 0, Chalakim: 7.*/
        moladDate = JewishDate.now() 
        moladDate.setJewishDateByMolad(getChalakimSinceMoladTohu(this._jyear, this._jmonth))
        if (moladDate.molad_hours >= 6){
            moladDate.forward()
        }
        moladDate._molad_hours = (moladDate.molad_hours + 18) % 24
        return moladDate
    }

    moladToAbsDate(chalakim){
        //Returns the number of days from the Jewish epoch from the number of chalakim from the epoch passed in.//
        return Math.floor((chalakim / CHALAKIM_PER_DAY) + JEWISH_EPOCH)
    }

    setJewishDateByMolad(molad){
        /*Sets JewishDate based on a molad passed in. The molad would be the number of chalakim/parts
        starting at the begining of Sunday prior to the molad Tohu BeHaRaD (Be = Monday, Ha= 5 hours and Rad =204
        chalakim/parts) - prior to the start of the Jewish calendar. BeHaRaD is 23:11:20 on
        Sunday night(5 hours 204/1080 chalakim after sunset on Sunday evening).*/
        this.fromordinal(this.moladToAbsDate(molad))
        let [conjunctionDay, conjunctionParts] = divmod(molad, CHALAKIM_PER_DAY)
        this.setMoladTime(conjunctionParts)
    }

    setMoladTime(chalakim){
        //Sets the molad time (hours minutes and chalakim) based on the number of chalakim since the start of the day.//
        [this._molad_hours, chalakim] = divmod(chalakim, CHALAKIM_PER_HOUR)
        [this._molad_minutes, this._molad_chalakim] = divmod(chalakim, CHALAKIM_PER_MINUTE)
    }

    get molad_hours(){
        //Molad Hours. Returns null if not set
        return this._molad_hours;
    }

    get molad_minutes(){
        //Molad Minutes. Returns null if not set
        return this._molad_minutes
    }

    get molad_chalakim(){
        //Molad Chalakim. Returns null if not set
        return this._molad_chalakim
    }

    constructor(jyear, jmonth, jday){
        if (Object.prototype.toString.call(jyear) === '[object Date]'){
            this.setDate(jyear);
        } else{
            this.setJewishDate(jyear, jmonth, jday);
        }
    }

    setDate(date){
        //Sets the date based on datetime object. Modifies the Jewish date as well.
        this.date = date;
        [this._jyear, this._jmonth, this._jday] = JewishDate.datetimeToJewishDate(date);
    }

    setGregorianDate(year, month, day, hour,
                minute, second, microsecond){
        //Return a new JewishDate object with new values for the specified fields. given in gregorian
        this.setDate(new Date(year, month, day, hour, minute, second, microsecond))
    }

    setJewishDate(year, month, day, hours, minutes, chalakim){
        /*Sets the Jewish Date and updates the Gregorian date accordingly.

        Arguments:
        year -- the Jewish year. The year can't be negative
        month -- the Jewish month. Nissan = 1 Adar II = 13
        day -- the Jewish day of month
        hours -- the hour of the day. Used for Molad calculations
        minutes -- the minutes. Used for Molad calculations
        chalakim -- the chalakim/parts. Used for Molad calculations. munt be less than 17

        throw news a ValueError if a A Jewish date earlier than 18 Teves, 3761 (1/1/1 Gregorian),
        a month < 1 or > 12 (or 13 on a leap year), the day of month is < 1 or > 30, an hour < 0 or > 23,
        a minute < 0 > 59 or chalakim < 0 > 17. For larger a larger number of chalakim such as 793 (TaShTzaG)
        break the chalakim into minutes (18 chalakim per minutes, so it would be 44 minutes and 1 chelek in
        the case of 793 (TaShTzaG).*/
        if (!hours){
            JewishDate.validateJewishDate(year, month, day, 0, 0, 0)
        } else {
            JewishDate.validateJewishDate(year, month, day, hours, minutes, chalakim)
        }

        this._molad_hours = hours
        this._molad_minutes = minutes
        this._molad_chalakim = chalakim

        let absDate = JewishDate.jewishDateToAbsDate(year, month, day) // reset Gregorian date
        this.date = absDateToDate(absDate)
        this._jyear = year
        this._jmonth = month
        this._jday = day
    }

    static now(){
        //Creates Jewish Date set to current system time//
        return new JewishDate(new Date())
    }

    toString(){
        /*Returns a string containing the Jewish date in the form, "day Month, year" e.g. "21 Shevat, 5729". For more
        complex formatting, use the formatter classes.*/
        return new HebrewDateFormatter().format_date(this)
    }

    forward(){
        //Rolls Date forward 1 day//
        this.date.setDate(this.date.getDate() + 1);
        if (this._jday < 29){
            this._jday += 1
        } else if (this._jday === getDaysInJewishMonth(this._jmonth, this._jyear)){
            this._jday = 1
            if (this._jmonth == 6){
                this._jyear += 1
                this._jmonth = 7
            } else if (this._jmonth == 12){
                if (JewishDate.isJewishLeapYear(this._jyear)){
                    this._jmonth = 13
                } else{
                    this._jmonth = 1
                }
            } else if (this._jmonth === 13){
                this._jmonth = 1
            } else {
                this._jmonth += 1
            }
        } else if (this._jday === 29){
            this._jday += 1
        } else{
            throw new ValueError("Date is Wrong")
        }
    }

    back(){
        //Rolls Date back 1 day//
        this.date.setDate(this.date.getDate() - 1); 
        if (this._jday > 1){
            this._jday -= 1
        } else {
            if (this._jmonth === 7){
                this._jyear -= 1
                this._jmonth -=1
            } else if (this._jmonth === 1){
                if (JewishDate.isJewishLeapYear(this._jyear)){
                    this._jmonth = 13
                } else {
                    this._jmonth = 12
                }
            } else {
                this._jmonth -= 1
            }
            this._jday = getDaysInJewishMonth(this._jmonth, this._jyear)
        }
    }

   get gyear(){
        //Gregorian Year
        return this.date.getFullYear()
   }

    get gmonth(){
        //Gregorian Month
        return this.date.getMonth()
    }

    get gday(){
        //Gregorian Day//
        return this.date.getDate()
    }

    get jyear(){
        //Jewish Year//
        return this._jyear
    }

    get jmonth(){
        //Jewish Month - Nissan = 1, Adar II = 13
        return this._jmonth
    }

    get jday(){
        //Jewish Day
        return this._jday
    }

    get dayofweek(){
        //Day of the week as a number between Sunday=1, Saturday=7.//
        return this.date.getDay() + 1
    }

    getDay(){
        //Return the day of the week as a number between Monday=1, Sunday=7.//
        return this.date.getDay()
    }
    /*    
    weekday(){
        //Return datetime.weekday()
        return this.dt.weekday()
    }
    */
    /*
    greplace(year=null, month=null, day=null, hour=null,
                minute=null, second=null, microsecond=null, tzinfo=True):
        //Return a new JewishDate object with new values for the specified fields. given in gregorian//
        return JewishDate(this.dt.replace(year, month, day, hour, minute, second, microsecond, tzinfo))

    jreplace(jyear=null, jmonth=null, jday=null):
        /*Return a new JewishDate with new values for the specified fields.
        jyear -- must be between greater than 3761 (or 3761 if after 18 Teves)
        jmonth -- Nissan = 1 and Adar II = 13
        jday -- the day of the month
        jyear = jyear || this._jyear
        jmonth = jmonth || this._jmonth
        jday = jday || this._jday
        return JewishDate(jyear, jmonth, jday)
        */
}

const Sat_short = [null, 52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 53, 23, 24, null, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47,
            48, 49, 50]
const Sat_long = [null, 52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 53, 23, 24, null, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47,
            48, 49, 59]
const Mon_short = [51, 52, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
            18, 19, 20, 53, 23, 24, null, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47, 48,
            49, 59]
const Mon_long = [51, 52, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 53, 23, 24, null, 25, 54, 55,
            30, 56, 33, null, 34, 35, 36, 37, 57, 40, 58, 43, 44, 45, 46, 47, 48, 49, 59 ] //split
const Thu_normal = [52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
            18, 19, 20, 53, 23, 24, null, null, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47,
            48, 49, 50 ]
const Thu_normal_Israel = [52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 53, 23, 24, null, 25, 54, 55, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 58, 43, 44, 45,
            46, 47, 48, 49, 50]
const Thu_long = [52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
            18, 19, 20, 21, 22, 23, 24, null, 25, 54, 55, 30, 56, 33, 34, 35, 36, 37, 38, 39, 40, 58, 43, 44, 45, 46, 47,
            48, 49, 50]
const Sat_short_leap = [null, 52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, null, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 58,
            43, 44, 45, 46, 47, 48, 49, 59]
const Sat_long_leap = [null, 52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, null, 28, 29, 30, 31, 32, 33, null, 34, 35, 36, 37, 57, 40, 58,
            43, 44, 45, 46, 47, 48, 49, 59]
const Mon_short_leap = [51, 52, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, null, 28, 29, 30, 31, 32, 33, null, 34, 35, 36, 37, 57, 40, 58, 43,
            44, 45, 46, 47, 48, 49, 59]
const Mon_short_leap_Israel = [51, 52, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
            15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, null, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
            58, 43, 44, 45, 46, 47, 48, 49, 59]
const Mon_long_leap = [51, 52, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, null, null, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 58,
            43, 44, 45, 46, 47, 48, 49, 50]
const Mon_long_leap_Israel = [51, 52, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
            15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, null, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
            41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
const Thu_short_leap = [52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, null, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
            43, 44, 45, 46, 47, 48, 49, 50]
const Thu_long_leap = [52, null, null, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, null, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
            43, 44, 45, 46, 47, 48, 49, 59]
                    
const parsha_array_diaspora = {"2 - 0 - False": Mon_short,
                        "2 - 2 - False": Mon_long,
                        "3 - 1 - False": Mon_long,
                        "5 - 1 - False": Thu_normal,
                        "5 - 2 - False": Thu_long,
                        "7 - 0 - False": Sat_short,
                        "7 - 2 - False": Sat_long,
                        "2 - 0 - True": Mon_short_leap,
                        "2 - 2 - True": Mon_long_leap,
                        "3 - 1 - True": Mon_long_leap,
                        "5 - 0 - True": Thu_short_leap,
                        "5 - 2 - True": Thu_long_leap,
                        "7 - 0 - True": Sat_short_leap,
                        "7 - 2 - True": Sat_long_leap}

const parsha_array_israel = {"2 - 0 - False": Mon_short,
                        "2 - 2 - False": Mon_short,
                        "3 - 1 - False": Mon_short,
                        "5 - 1 - False": Thu_normal_Israel,
                        "5 - 2 - False": Thu_long,
                        "7 - 0 - False": Sat_short,
                        "7 - 2 - False": Sat_long,
                        "2 - 0 - True": Mon_short_leap_Israel,
                        "2 - 2 - True": Mon_long_leap_Israel,
                        "3 - 1 - True": Mon_long_leap_Israel,
                        "5 - 0 - True": Thu_short_leap,
                        "5 - 2 - True": Thu_long_leap,
                        "7 - 0 - True": Sat_short_leap,
                        "7 - 2 - True": Sat_short_leap}

const holidays_diaspora = {"1 - 14": 0,  // EREV_PESACH
                "1 - 15": 1,  // PESACH
                "1 - 16": 1,  // PESACH
                "1 - 17": 2,  // CHOL_HAMOED_PESACH
                "1 - 18": 2,  // CHOL_HAMOED_PESACH
                "1 - 19": 2,  // CHOL_HAMOED_PESACH
                "1 - 20": 2,  // CHOL_HAMOED_PESACH
                "1 - 21": 1,  // PESACH
                "1 - 22": 1,  // PESACH
                "2 - 14": 3,  // PESACH_SHENI
                "2 - 18": 33,  // LAG_BAOMER
                "3 - 5": 4,  // EREV_SHAVUOS
                "3 - 6": 5,  // SHAVUOS
                "3 - 7": 5,  // SHAVUOS
                "5 - 15": 8,  // TU_BEAV
                "6 - 29": 9,  // EREV_ROSH_HASHANA
                "7 - 1": 10,  // ROSH_HASHANA
                "7 - 2": 10,  // ROSH_HASHANA
                "7 - 9": 12,  // EREV_YOM_KIPPUR
                "7 - 10": 13,  // YOM_KIPPUR
                "7 - 14": 14,  // EREV_SUCCOS
                "7 - 15": 15,  // SUCCOS
                "7 - 16": 15,  // SUCCOS
                "7 - 17": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 18": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 19": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 20": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 21": 17,  // HOSHANA_RABBA
                "7 - 22": 18,  // SHEMINI_ATZERES
                "7 - 23": 19,  // SIMCHAS_TORAH
                //"9 - 24": 20,  // EREV_CHANUKAH
                "9 - 25": 21,  // CHANUKAH
                "9 - 26": 21,  // CHANUKAH
                "9 - 27": 21,  // CHANUKAH
                "9 - 28": 21,  // CHANUKAH
                "9 - 29": 21,  // CHANUKAH
                "9 - 30": 21,  // CHANUKAH - Though doesnt always exist - it is always chanuka
                "10 - 1": 21,  // CHANUKAH
                "10 - 2": 21,  // CHANUKAH
                "10 - 10": 22,  // TENTH_OF_TEVES
                "11 - 15": 23,  // TU_BESHEVAT
                "13 - 14": 25,  // PURIM
                "13 - 15": 26}  // SHUSHAN_PURIM

const holidays_israel = {"1 - 14": 0,  // EREV_PESACH
                "1 - 15": 1,  // PESACH
                "1 - 16": 2,  // CHOL_HAMOED_PESACH
                "1 - 17": 2,  // CHOL_HAMOED_PESACH
                "1 - 18": 2,  // CHOL_HAMOED_PESACH
                "1 - 19": 2,  // CHOL_HAMOED_PESACH
                "1 - 20": 2,  // CHOL_HAMOED_PESACH
                "1 - 21": 1,  // PESACH
                "2 - 14": 3,  // PESACH_SHENI
                "2 - 18": 33,  // LAG_BAOMER
                "3 - 5": 4,  // EREV_SHAVUOS
                "3 - 6": 5,  // SHAVUOS
                "5 - 15": 8,  // TU_BEAV
                "6 - 29": 9,  // EREV_ROSH_HASHANA
                "7 - 1": 10,  // ROSH_HASHANA
                "7 - 2": 10,  // ROSH_HASHANA
                "7 - 9": 12,  // EREV_YOM_KIPPUR
                "7 - 10": 13,  // YOM_KIPPUR
                "7 - 14": 14,  // EREV_SUCCOS
                "7 - 15": 15,  // SUCCOS
                "7 - 16": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 17": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 18": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 19": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 20": 16,  // CHOL_HAMOED_SUCCOS
                "7 - 21": 17,  // HOSHANA_RABBA
                "7 - 22": 18,  // SHEMINI_ATZERES
                //"9 - 24": 20,  // EREV_CHANUKAH
                "9 - 25": 21,  // CHANUKAH
                "9 - 26": 21,  // CHANUKAH
                "9 - 27": 21,  // CHANUKAH
                "9 - 28": 21,  // CHANUKAH
                "9 - 29": 21,  // CHANUKAH
                "9 - 30": 21,  // CHANUKAH - Though doesnt always exist - it is always chanuka
                "10 - 1": 21,  // CHANUKAH
                "10 - 2": 21,  // CHANUKAH
                "10 - 10": 22,  // TENTH_OF_TEVES
                "11 - 15": 23,  // TU_BESHEVAT
                "13 - 14": 25,  // PURIM
                "13 - 15": 26}  // SHUSHAN_PURIM

const fast_days_nidche = {"4 - 18 - 1": 6,  // SEVENTEEN_OF_TAMMUZ
                "5 - 10 - 1": 7,  // TISHA_BEAV
                "7 - 4 - 1": 11,  // FAST_OF_GEDALYAH
                "13 - 11 - 5": 24,  // FAST_OF_ESTHER
                "13 - 12 - 5": 24}  // FAST_OF_ESTHER

const fast_days_normal = {"4 - 17": 6,  // SEVENTEEN_OF_TAMMUZ
                "5 - 9": 7,  // TISHA_BEAV
                "7 - 3": 11,  // FAST_OF_GEDALYAH
                "13 - 13": 24}  // FAST_OF_ESTHER

const modern_holidays = {"1 - 26 - 5": 29,  // YOM_HASHOAH
                "1 - 27 - 3": 29,  // YOM_HASHOAH
                "1 - 27 - 7": 29,  // YOM_HASHOAH
                "1 - 28 - 3": 29,  // YOM_HASHOAH
                "2 - 2 - 4": 30,  // YOM_HAZIKARON
                "2 - 3 - 4": 30,  // YOM_HAZIKARON
                "2 - 4 - 3": 30,  // YOM_HAZIKARON
                "2 - 5 - 2": 30,  // YOM_HAZIKARON
                "2 - 3 - 5": 31,  // YOM_HAATZMAUT
                "2 - 4 - 5": 31,  // YOM_HAATZMAUT
                "2 - 5 - 4": 31,  // YOM_HAATZMAUT
                "2 - 6 - 3": 31,  // YOM_HAATZMAUT
                "2 - 28 - 1": 32,  // YOM_YERUSHALAYIM
                "2 - 28 - 2": 32,  // YOM_YERUSHALAYIM
                "2 - 28 - 3": 32,  // YOM_YERUSHALAYIM
                "2 - 28 - 4": 32,  // YOM_YERUSHALAYIM
                "2 - 28 - 5": 32,  // YOM_YERUSHALAYIM
                "2 - 28 - 6": 32,  // YOM_YERUSHALAYIM
                "2 - 28 - 7": 32}  // YOM_YERUSHALAYIM
const EREV_PESACH = 0
const PESACH = 1
const CHOL_HAMOED_PESACH = 2
const PESACH_SHENI = 3
const EREV_SHAVUOS = 4
const SHAVUOS = 5
const SEVENTEEN_OF_TAMMUZ = 6
const TISHA_BEAV = 7
const TU_BEAV = 8
const EREV_ROSH_HASHANA = 9
const ROSH_HASHANA = 10
const FAST_OF_GEDALYAH = 11
const EREV_YOM_KIPPUR = 12
const YOM_KIPPUR = 13
const EREV_SUCCOS = 14
const SUCCOS = 15
const CHOL_HAMOED_SUCCOS = 16
const HOSHANA_RABBA = 17
const SHEMINI_ATZERES = 18
const SIMCHAS_TORAH = 19
// EREV_CHANUKAH = 20// probably remove this
const CHANUKAH = 21
const TENTH_OF_TEVES = 22
const TU_BESHEVAT = 23
const FAST_OF_ESTHER = 24
const PURIM = 25
const SHUSHAN_PURIM = 26
const PURIM_KATAN = 27
const ROSH_CHODESH = 28
const YOM_HASHOAH = 29
const YOM_HAZIKARON = 30
const YOM_HAATZMAUT = 31
const YOM_YERUSHALAYIM = 32
const LAG_BAOMER = 33
const dafYomiStartDate = new Date(1923, 9, 11)
const shekalimChangeDate = new Date(1975, 6, 24)

class JewishCalendar extends JewishDate{
    /*reates a Jewish Calendar object which extends the JewishDate class

    Arguments:
    year -- can be a Date object - then all other arguments are disregarded
    year -- the Jewish year. The year can't be negative
    month -- the Jewish month. Nissan = 1 Adar II = 13
    day -- the Jewish day of month
    
    This open source Python code was originally ported to Java by <a href="http//www.facebook.com/avromf">Avrom Finkelstien</a>
    from his C++ code. It was refactored to fit the KosherJava Zmanim API with simplification of the code, enhancements
    and some bug fixing. It was then ported to Python.
    The methods used to obtain the parsha were derived from the source code of
    <a href="http//www.sadinoff.com/hebcal/">HebCal</a> by Danny Sadinoff and JCal for the Mac by Frank Yellin. Both based
    their code on routines by Nachum Dershowitz and Edward M. Reingold. The class allows setting whether the parsha and
    holiday scheme follows the Israel scheme or outside Israel scheme. The default is the outside Israel scheme.
    
    TODO: Some do not belong in this class, but here is a partial list of what should still be implemented in some form:
    * Add Isru Chag
    * Add special parshiyos (shekalim, parah, zachor and hachodesh
    * Shabbos Mevarchim
    * Haftorah (various minhagim)
    * Daf Yomi Yerushalmi, Mishna yomis etc)
    * Support showing the upcoming parsha for the middle of the week

    Author: Avrom Finkelstien 2002
    Author: Eliyahu Hershfeld 2011 - 2012
    Version: 0.0.1*/

    constructor(date, jmonth, jday, opts){
        super(date, jmonth, jday)
        opts = opts || {}
        this.in_israel = opts.inIsrael || false
        this.use_modern_holidays = opts.modernHolidaysfalse || false
        this.not_holiday = false
        this.holiday_index = null
        this.not_holiday = false // only for optimization - will not always be correct
    }
        
    static now(){
        //Creates Jewish Calendar set to current system time
        return new JewishCalendar(new Date())
    }
        
    setJewishDateByMolad(molad){
        super.setJewishDateByMolad(molad)
        this.not_holiday = false
        this.holiday_index = null
    }
        
    setDate(dt){
        super.setDate(dt)
        this.not_holiday = false
        this.holiday_index = null
    }
        
    setGregorianDate(year, month, day, hour,
                    minute, second, microsecond){
        super.setGregorianDate(year, month, day, hour,
                    minute, second, microsecond)
        this.not_holiday = false
        this.holiday_index = null
    }
                    
    setJewishDate(year, month, day, hours, minutes, chalakim){
        super.setJewishDate(year, month, day, hours, minutes, chalakim)
        this.not_holiday = false
        this.holiday_index = null
    }
        
    forward(){
        super.forward()
        this.not_holiday = false
        this.holiday_index = null
    }
        
    back(){
        super.back()
        this.not_holiday = false
        this.holiday_index = null
    }

    getYomTovIndex(){
        //Return an index if current day is a Jewish holiday/fast day, or null if not//
        let index = null
        if (this.not_holiday){
            return null
        }
        if (this.holiday_index){
            return this.holiday_index
        }
        if (!this.in_israel){
            index = holidays_diaspora[this.jmonth + " - " + this.jday] || null
        } else {
            index = holidays_israel[this.jmonth + " - " + this.jday] || null
        }
        index = fast_days_nidche[this.jmonth + " - " + this.jday + " - " + this.dayofweek] || index
        if (!index){  // can probably be made into one line
            index = fast_days_normal[this.jmonth + " - " + this.jday] || null
        }
        if (this.use_modern_holidays){
            index = modern_holidays[this.jmonth + " - " + this.jday + " - " + this.dayofweek] || index
        }
        if (!index){
            if (this.jmonth == TEVES){
                if (JewishDate.isKislevShort(self._jyear) && this.jday == 3){
                    this.holiday_index = CHANUKAH
                    return CHANUKAH
                }
            }
            if (this.jmonth == ADAR && !JewishDate.isJewishLeapYear(this._jyear)){
                if (this.jday == 11 || this.jday == 12 && this.dayofweek == 5){
                    this.holiday_index = FAST_OF_ESTHER
                    return FAST_OF_ESTHER
                } else if (this.jday == 13 && !this.dayofweek >= 6){
                    this.holiday_index = FAST_OF_ESTHER
                    return FAST_OF_ESTHER
                }
                if (this.jday == 14){
                    this.holiday_index = PURIM
                    return PURIM
                }
                if (this.jday == 15){
                    this.holiday_index = SHUSHAN_PURIM
                    return SHUSHAN_PURIM
                }
            } else if (this.jmonth == ADAR && JewishDate.isJewishLeapYear(this._jyear)){
                if (this.jday == 14){
                    this.holiday_index = PURIM_KATAN
                    return PURIM_KATAN
                }
            }
            this.not_holiday = true
            return null  // no Yom Tov
        }
        this.holiday_index = index
        return index
    }

    isYomTov(){
        //Return true if the current day is Yom Tov. The method returns false for Chanukah, Erev Yom tov and fast days.//
        let holidayIndex = this.getYomTovIndex()
        if (this.isErevYomTov() || holidayIndex == CHANUKAH || (this.isTaanis() && !(holidayIndex == YOM_KIPPUR))){
            return false
        }
        return Boolean(holidayIndex)
    }

    isCholHamoed(){
        //Return True if the current day is Chol Hamoed of Pesach or Succos.//
        let holidayIndex = this.getYomTovIndex()
        return holidayIndex == CHOL_HAMOED_PESACH || holidayIndex == CHOL_HAMOED_SUCCOS
    }

    isErevYomTov(){
        /*Return True if the current day is erev Yom Tov. The method returns true for Erev Pesach, Shavuos, Rosh
        Hashana, Yom Kippur and Succos.*/
        let holidayIndex = this.getYomTovIndex()
        return holidayIndex == EREV_PESACH || holidayIndex == EREV_SHAVUOS || holidayIndex == EREV_ROSH_HASHANA || holidayIndex == EREV_YOM_KIPPUR || holidayIndex == EREV_SUCCOS
    }

    isErevRoshChodesh(){
        //Return True if the current day is Erev Rosh Chodesh. Returns False for Erev Rosh Hashana//
        return this.jday == 29 && this.jmonth != ELUL
    }

    isTaanis(){
        //Return True if the day is a Taanis (fast day).//
        let holidayIndex = this.getYomTovIndex()
        return holidayIndex == SEVENTEEN_OF_TAMMUZ || holidayIndex == TISHA_BEAV || holidayIndex == YOM_KIPPUR || holidayIndex ==  FAST_OF_GEDALYAH || holidayIndex == TENTH_OF_TEVES || holidayIndex == FAST_OF_ESTHER
    }

    getDayOfChanukah(){
        //Returns the day of Chanukah or null if it is not Chanukah.//
        if (this.isChanukah()){
            if (this.jmonth == KISLEV){
                return this.jday - 24
            } else{ // teves
                if (JewishDate.isKislevShort(this._jyear)){
                    return this.jday + 5
                }
                return this.jday + 6
            }
        }
        return null
    }

    isChanukah(){
        return this.getYomTovIndex() == CHANUKAH
    }

    getParshaIndex(){
        /*Return a the index of today's parsha(ios) or a -1 if there is null. To get the name of the Parsha, use the
        HebrewDateFormatter

        NOTE: This only returns the parsha for Shabbos - not the upcoming shabbos's parsha */
        //
        // if today is not Shabbos, then there is no normal parsha reading. If
        // commented our will return LAST week's parsha for a non shabbos
        if (this.dayofweek != 7){
            return null
        }
        // kvia = whether a Jewish year is short/regular/long (0/1/2)
        // roshHashana = Rosh Hashana of this Jewish year
        // roshHashanaDay= day of week Rosh Hashana was on this year
        // week= current week in Jewish calendar from Rosh Hashana
        let kvia = JewishDate.getCheshvanKislevKviah(this.jyear)
        let roshHashana = new JewishDate(this.jyear, TISHREI, 1) // set it to Rosh Hashana of this year
        let roshHashanaDay = roshHashana.dayofweek
        // week is the week since the first Shabbos on or after Rosh Hashana
        let week = Math.floor(((this.date.toordinal() - roshHashana.date.toordinal()) - (7 - roshHashanaDay)) / 7)
        let array = null
        // determine appropriate array
        if (this.in_israel){
            array = parsha_array_israel[roshHashanaDay + " - " + kvia + " - " + (JewishDate.isJewishLeapYear(this._jyear) ? "True" : "False")] || null
         } else {
            array = parsha_array_diaspora[roshHashanaDay + " - " + kvia + " - " + (JewishDate.isJewishLeapYear(this._jyear) ? "True" : "False")] || null
         }
        if (!array){
            throw new ValueError("Unable to calculate the parsha. No index array matched any of the known types for the date: " + toString(this))
        }
        return array[week]
    }

    isRoshChodesh(){
        //Return True if the day is Rosh Chodesh. Rosh Hashana will return False//
        // Rosh Hashana is not rosh chodesh. Elul never has 30 days
        return this.jday == 1 && this.jmonth != TISHREI || this.jday == 30
    }

    getDayOfOmer(){
        //Return the int value of the Omer day or -1 if the day is not in the omer//
        // if Nissan and second day of Pesach and on
        if (this.jmonth == NISSAN && this.jday >= 16){
            return this.jday - 15
        }
        // if Iyar
        if (this.jmonth == IYAR){
            return this.jday + 15
        }
        // if Sivan and before Shavuos
        if (this.jmonth == SIVAN && this.jday < 6){
            return this.jday + 44
        }
        return null
    }

    getDafYomiBavli(){
        //Return tuple of Mesechta number and Daf of the days Daf Yomi//
        //The number of daf per masechta. Since the number of blatt in Shekalim changed on the 8th Daf Yomi cycle
        //beginning on June 24, 1975 from 13 to 22, the actual calculation for blattPerMasechta[4] will later be
        //adjusted based on the cycle.
        let blattPerMasechta = [64, 157, 105, 121, 22, 88, 56, 40, 35, 31, 32, 29, 27, 122, 112, 91, 66, 49, 90, 82,
                119, 119, 176, 113, 24, 49, 76, 14, 120, 110, 142, 61, 34, 34, 28, 22, 4, 10, 4, 73]
        let date = this.date
        let dafYomi = null
        let cycleNo = 0
        let dafNo = 0
        if (date < dafYomiStartDate){
            // TODO: should we return a null or throw an Value error?
            throw new ValueError(date + " is prior to organized Daf Yomi Bavli cycles that started on " + dafYomiStartDate)
        }
        if (date >= this.shekalimChangeDate){
            cycleNo, dafNo = divmod(date.toordinal() - new Date(1975, 6, 24).toordinal(), 2711)
            cycleNo += 8
        } else {
            cycleNo, dafNo = divmod(date.toordinal() - new Date(1923, 9, 11).toordinal(), 2702)
            cycleNo += 1
        }

        let total = 0
        let masechta = -1
        let blatt = 0

        // Fix Shekalim for old cycles.//
        if (cycleNo <= 7){
            blattPerMasechta[4] = 13
        } else{
            blattPerMasechta[4] = 22 // correct any change that may have been changed from a prior calculation
        }

        // Finally find the daf.//

        for (let j = 0; j < blattPerMasechta.length; j++){
            masechta += 1 //why is this necesar - isnt it the same as j
            total = total + blattPerMasechta[j] - 1
            if (dafNo < total){
                blatt = 1 + blattPerMasechta[j] - (total - dafNo)
                // Fiddle with the weird ones near the end.//
                if (masechta == 36){
                    blatt += 21
                } else if (masechta == 37){
                    blatt += 24
                } else if (masechta == 38){
                    blatt += 33
                }
                return masechta, blatt
            }
        }
    }
                
}
