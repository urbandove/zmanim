const NISSAN:i64 = 1;
const IYAR:i64 = 2;
//const SIVAN:i64 = 3;
const TAMUZ:i64 = 4;
//const AV:i64 = 5;
const ELUL:i64 = 6;
const TISHREI:i64 = 7;
const CHESHVAN:i64 = 8;
const KISLEV:i64 = 9;
const TEVES:i64 = 10;
//const SHEVAT:i64 = 11;
const ADAR:i64 = 12;
const ADAR_II:i64 = 13;
const JEWISH_EPOCH:i64 = -1373429;  // Jewish Epoch. Day 1 is Jan 1, 01 Gregorian. From Calendrical Calculations
//const CHALAKIM_PER_MINUTE:i64 = 18;
//const CHALAKIM_PER_HOUR:i64 = 1080;
const CHALAKIM_PER_DAY:i64 = 25920; // 24 * 1080
const CHALAKIM_PER_MONTH:i64 = 765433; // (29 * 24 + 12) * 1080 + 793
const CHALAKIM_MOLAD_TOHU:i64 = 31524;  // Chalakim from the beginning of Sunday till molad BaHaRaD.
//const CHASERIM:i64 = 0;  // Cheshvan and Kislev both 29 days
//const KESIDRAN:i64 = 1;  // Cheshvan 29 days and Kislev 30 days
//const SHELAIMIM:i64 = 2;  // Cheshvan and Kislev both 30 days
const END_GMONTH_DAYS:[i64;14] = [0,0,31,59,90,120,151,181,212,243,273,304,334,365];

fn divmod(numerator:i64,denominator :i64)-> (i64, i64){
    return (numerator/denominator, numerator%denominator)
}

fn is_jyear_leap(year: i64)-> bool{
    return ((7 * year) + 1) % 19 < 7;
}

fn get_jmonth_of_year(year: i64, month:i64) -> i64{
    //Converts the Nissan based months used by this class to numeric month starting from Tishrei.
    //This is required for Molad claculations.
    
    return if is_jyear_leap(year) {(month + 6) % 13 + 1} else {(month + 5) % 12 + 1}
}

fn get_rh_day(year:i64) -> i64{
    //Returns the number of days elapsed from the Sunday prior to the start of the Jewish calendar
    //to the mean conjunction of Tishri of the Jewish year.
    //Jewish lunar month = 29 days, 12 hours and 793 chalakim
    //chalakim since Molad Tohu BeHaRaD - 1 day, 5 hours and 204 chalakim
    let year_in_cycle = (year - 1) % 19;
    let months = (year - 1) / 19 * 235 // Months in complete 19 year lunar (Metonic) cycles so far
                + year_in_cycle * 12 // Regular months in this cycle
                + (7 * year_in_cycle + 1) / 19 // Leap months this cycle
                + get_jmonth_of_year(year, TISHREI) - 1;  //  add months since start of year
    // return chalakim prior to BeHaRaD + number of chalakim since
    let chalakim_since = CHALAKIM_MOLAD_TOHU + (CHALAKIM_PER_MONTH * months);
    let (mut rosh_hashana_day, molad_parts) = divmod(chalakim_since, CHALAKIM_PER_DAY);
    // delay Rosh Hashana for the 4 dechiyos
    //roshHashanaDay = moladDay // if no dechiyos
    // delay Rosh Hashana for the dechiyos of the Molad - new moon
    // 1 - Molad Zaken, 2- GaTRaD 3- BeTuTaKFoT
    if molad_parts >= 19440{ // Molad Zaken Dechiya - molad is >= midday (18 hours * 1080 chalakim)
        rosh_hashana_day += 1; // Then postpone Rosh HaShanah one day
    } else {
        let temp = rosh_hashana_day % 7;
        if ((temp == 2) // start Dechiya of GaTRaD - Ga = is a Tuesday
             && (molad_parts >= 9924) // TRaD = 9 hours, 204 parts or later (9 * 1080 + 204)
             && (!is_jyear_leap(year))) // of a non-leap year - end Dechiya of GaTRaD
                || ((temp == 1) // start Dechiya of BeTuTaKFoT - Be = is on a Monday
                    && (molad_parts >= 16789) // TRaD >= 15 hours, 589 parts (15 * 1080 + 589)
                    && (is_jyear_leap(year - 1))){ // year following a leap year - no BeTuTaKFoT
                        rosh_hashana_day += 1; // Then postpone Rosh HaShanah one day
                    }
    }
    // start 4th Dechiya - Lo ADU Rosh - Rosh Hashana can't occur on A- Sun, D- Wed, U - Fri
    match rosh_hashana_day %7 {
        0 | 3 | 5 => rosh_hashana_day += 1,
        _ => (),
    }
    return rosh_hashana_day;
}

fn get_days_in_jyear(year: i64) -> i64{
    //"""Returns the number of days for a given Jewish year. ND+ER"""
    return get_rh_day(year + 1) - get_rh_day(year)
}

fn is_cheshvan_long(year: i64) -> bool{
    //"""Returns if Cheshvan is long in a given Jewish year."""
    return get_days_in_jyear(year) % 10 == 5;
}

fn is_kislev_short(year: i64) -> bool{
    //"""Returns if Kislev is short (29 days VS 30 days) in a given Jewish year."""
    return get_days_in_jyear(year) % 10 == 3;
}

fn get_days_cheshvan_kislev(year: i64)-> (i64, i64){
    //"""Returns a tuple containing (days_in_cheshvan, days_in_kislev) for given year"""
    let days = get_days_in_jyear(year);
    let cheshvandays = if days % 10 == 5 {30} else {29};
    let kislevdays = if days % 10 == 3 {29} else {30};
    return (cheshvandays, kislevdays);
}

fn get_days_in_jmonth(month:i64, year:i64) -> i64{
    //"""Returns the number of days of a Jewish month for a given month and year."""
    match month{
        IYAR | TAMUZ | ELUL | TEVES | ADAR_II =>  return 29,
        CHESHVAN => return if is_cheshvan_long(year) {30} else {29},
        KISLEV => return if is_kislev_short(year) {29} else {30},
        ADAR => return if is_jyear_leap(year) {30} else {29},
        _ => return 30
    }
}

fn jdate_to_abs_date(year: i64, month: i64, day: i64) -> i64{
    //Returns the absolute date of Jewish date. ND+ER
    //Arguments:
    //year -- Jewish year. The year can't be negative
    //month -- Nissan =1 and Adar II = 13
    //day -- day of month
    
    let mut elapsed_days = day;
    // Before Tishrei (from Nissan to Tishrei), add days in prior months
    if month < TISHREI{
        // this year before and after Nisan.
        for mon in TISHREI..(if is_jyear_leap(year) {ADAR_II} else {ADAR} +1){
            elapsed_days += get_days_in_jmonth(mon, year);
        }
        for mon in NISSAN.. month{
            elapsed_days += get_days_in_jmonth(mon, year);
        }
    } else{// Add days in prior months this year
        for mon in TISHREI..month{
            elapsed_days += get_days_in_jmonth(mon, year);
        }
    }
    // add elapsed days this year + Days in prior years + Days elapsed before absolute year 1
    return elapsed_days + get_rh_day(year) + JEWISH_EPOCH;
}


fn get_gdays_till_month_start(month:i64, year:i64)-> i64{
    if month > 2{
        if (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0) {
            return END_GMONTH_DAYS[month as usize] + 1;
        }
    }
    return END_GMONTH_DAYS[month as usize];
}

fn gdate_to_absdate(year:i64, month:i64, day: i64) -> i64{
		let abs_date = day + get_gdays_till_month_start(month, year);
		return abs_date // days this year
				+ 365 * (year - 1) // days in previous years ignoring leap days
				+ (year - 1) / 4 // Julian leap days before this year
				- (year - 1) / 100 // minus prior century years
		        + (year - 1) / 400; // plus prior years divisible by 400
}

fn absdate_to_gdate(abs_date: i64) -> (i64,i64,i64) {
		let mut year = abs_date / 366; // Search forward year by year from approximate year
		while abs_date >= gdate_to_absdate(year + 1, 1, 1){
			year += 1;
		}

		let mut month:i64 = 1; // Search forward month by month from January
        let remainder = abs_date - gdate_to_absdate(year, 1, 1);
        while get_gdays_till_month_start(month+1, year) < remainder{
            month += 1;
        }

		let day:i64 = abs_date - gdate_to_absdate(year, month, 1) + 1;
		return (year, month, day);
}


fn gdate_to_jdate(year: i64, month: i64, day:i64) -> (i64,i64,i64){
    //"""Computes the Jewish date from the absolute date. ND+ER"""
    let abs_date = gdate_to_absdate(year, month, day);
    // Start with approximation
    let mut jyear = year + 3760;
    // Search forward for year from the approximation
    let mut tempabsdate = jdate_to_abs_date(jyear + 1, TISHREI, 1);
    while abs_date >= tempabsdate{
        jyear += 1;
        if abs_date - tempabsdate < 353{
            break
        }
        tempabsdate = jdate_to_abs_date(jyear + 1, TISHREI, 1);
    }
    let is_leap_year = is_jyear_leap(jyear);
    //start with tishrei
    let mut jmonth = TISHREI;
    let mut daysbeyond0ofjmonth = abs_date - jdate_to_abs_date(jyear, jmonth, 1);
    let mut daysinjmonth = get_days_in_jmonth(jmonth, jyear);
    //go forward month by month
    while daysbeyond0ofjmonth >= daysinjmonth{
        jmonth += 1;
        if jmonth > 12{
            if !is_leap_year || jmonth == 14{
                jmonth = 1;
            }
        }
        daysbeyond0ofjmonth -= daysinjmonth;
        if jmonth == CHESHVAN{
            let (cheshvandays, kislevdays) = get_days_cheshvan_kislev(jyear);
            if daysbeyond0ofjmonth >= cheshvandays{
                jmonth += 1;
                daysbeyond0ofjmonth -= cheshvandays;
            }
            if daysbeyond0ofjmonth >= kislevdays{
                jmonth += 1;
                daysbeyond0ofjmonth -= kislevdays;
            }
        }
        daysinjmonth = get_days_in_jmonth(jmonth, jyear);
    }
    let jday = daysbeyond0ofjmonth + 1;
    return (jyear, jmonth, jday);
}

fn jdate_to_gdate(year:i64, month:i64, day:i64) -> (i64,i64,i64){
    return absdate_to_gdate(jdate_to_abs_date(year, month, day));
}


fn main(){
    let (year, month, day) = gdate_to_jdate(2017, 11, 27);
    let abs_date = gdate_to_absdate(2017, 11, 27);
    let (gyear, gmonth,gday) = absdate_to_gdate(736660);
    println!("hebyear: {} hebmonth: {} hebday:{}", year, month, day);
    println!("gyear: {} gmonth: {} gday:{}", gyear, gmonth, gday);
    let (ngyear, ngmonth, ngday) = jdate_to_gdate(5778,9,10);
    println!("jtog = gyear: {} gmonth: {} gday:{}", ngyear, ngmonth, ngday);
}
