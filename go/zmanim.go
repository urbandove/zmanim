package zmanim

import (
	"math"
	"time"
)

type Geolocation struct {
	Lat, Lon, Elevation float64
	Timezone            int //seconds ?is this needed - it seems the time struct holds timezones
}

/*type astronomical_calculator_defaults struct {
	geometric_zenith, civil_zenith, nautical_zenith, astronomical_zenith float64
}*/

const (
	julianDaysJan1_2000  = 2451545
	julianDaysPerCentury = 36525
	geometricZenith      = 90
	civilZenith          = 96
	nauticalZenith       = 102
	astronomicalZenith   = 108
	refraction           = 34.0 / 60.0
	solarRadius          = 16.0 / 60.0
	earthRadius          = 6356.9
)

type AstronomicalCalculator interface {
	sunrise() time.Time
	sealevelsunrise() time.Time
	sunset() time.Time
	sealevelsunset() time.Time
}

type NOAACalculator struct {
	Location Geolocation
	Time     time.Time
}

type SunTimesCalculator struct {
	Location Geolocation
	Time     time.Time
}

func getJulianDay(t time.Time) float64 {
	year, month, day := t.Year(), t.Month(), t.Day()
	if month <= 2 {
		year--
		month += 12
	}
	a := int(year / 100)
	b := 2 - a + int(a/4)
	c := year + 4716
	d := int(30.6001 * float64(month+1))
	jd := float64(b+365*c+int(c/4)+d+day) - 1524.5
	return jd
}

func toRadians(degrees float64) float64 {
	return degrees * (math.Pi / 180)
}

func toDegrees(radians float64) float64 {
	return radians * (180 / math.Pi)
}

func getTimeFromFloat(f float64, t time.Time) time.Time {
	hours := int(f)
	f -= float64(hours)
	f *= 60
	minutes := int(f)
	f -= float64(minutes)
	f *= 60
	seconds := int(f)
	f -= float64(seconds)
	f *= 1000000000
	nanoseconds := int(f)
	tUTC := t.UTC()
	//not sure if there is supposed to be a  + or minus a day depending on the offset (if f+offset > 24 minus a day and if < 0 add a day)
	newUTC := time.Date(tUTC.Year(), tUTC.Month(), tUTC.Day(), hours, minutes, seconds, nanoseconds, tUTC.Location())
	return newUTC.In(t.Location())
}

func getMeanObliquityOfEcliptic(julianCenturies float64) float64 {
	seconds := 21.448 - julianCenturies*(46.8150+julianCenturies*(0.00059-julianCenturies*0.001813))
	return 23 + (26+(seconds/60))/60 //returns degrees
}

func getObliquityCorrection(julianCenturies float64) float64 {
	obliquityOfEcliptic := getMeanObliquityOfEcliptic(julianCenturies)
	omega := 125.04 - 1934.136*julianCenturies
	return obliquityOfEcliptic + 0.00256*math.Cos(toRadians(omega)) //returns degrees
}

func getSunGeometricMeanLongitude(julianCenturies float64) float64 {
	lon := 280.46646 + julianCenturies*(36000.76983+0.0003032*julianCenturies)
	for lon > 360 {
		lon -= 360
	}
	for lon < 0 {
		lon += 360
	}
	return lon
}

func getSunGeometricMeanAnomaly(julianCenturies float64) float64 {
	return 357.52911 + julianCenturies*(35999.05029-0.0001537*julianCenturies) //returns degrees
}

func getEarthOrbitEccentricity(julianCenturies float64) float64 {
	return 0.016708634 - julianCenturies*(0.000042037+0.0000001267*julianCenturies) //unitless
}

func getSunEquationOfCenter(julianCenturies float64) float64 {
	m := toRadians(getSunGeometricMeanAnomaly(julianCenturies))
	sinm := math.Sin(m)
	sin2m := math.Sin(m * 2)
	sin3m := math.Sin(m * 3)
	return sinm*(1.914602-julianCenturies*(0.004817+0.000014*julianCenturies)) + sin2m*(0.019993-0.000101*julianCenturies) + sin3m*0.000289 // in degrees
}

func getSunTrueLongitude(julianCenturies float64) float64 {
	return getSunGeometricMeanLongitude(julianCenturies) + getSunEquationOfCenter(julianCenturies)
}

func getSunApparentLongitute(julianCenturies float64) float64 { //returns in degrees
	return getSunTrueLongitude(julianCenturies) - 0.00569 - 0.00478*math.Sin(toRadians(125.04-1934.136*julianCenturies))
}

func getSunDeclination(julianCenturies float64) float64 {
	a := math.Sin(toRadians(getObliquityCorrection(julianCenturies))) * math.Sin(toRadians(getSunApparentLongitute(julianCenturies)))
	return toDegrees(math.Asin(a))
}

func getJulianCenturiesFromJulianDay(jd float64) float64 {
	return (jd - julianDaysJan1_2000) / julianDaysPerCentury
}

func getJulianDayFromJulianCenturies(julianCenturies float64) float64 {
	return julianCenturies*julianDaysPerCentury + julianDaysJan1_2000
}

func getEquationOfTime(julianCenturies float64) float64 {
	eccentricityEarthsOrbit := getEarthOrbitEccentricity(julianCenturies)
	epsilon := toRadians(getObliquityCorrection(julianCenturies))
	geomMeanLongSun := toRadians(getSunGeometricMeanLongitude(julianCenturies))
	geomMeanAnamolySun := toRadians(getSunGeometricMeanAnomaly(julianCenturies))
	y := math.Pow(math.Tan(epsilon/2), 2)
	sin210 := math.Sin(2 * geomMeanLongSun)
	sinm := math.Sin(geomMeanAnamolySun)
	cos210 := math.Cos(2 * geomMeanLongSun)
	sin410 := math.Sin(4 * geomMeanLongSun)
	sin2m := math.Sin(2 * geomMeanAnamolySun)
	equationOfTime := y*sin210 - 2*eccentricityEarthsOrbit*sinm + 4*eccentricityEarthsOrbit*y*sinm*cos210 - 0.5*y*y*sin410 - 1.25*math.Pow(eccentricityEarthsOrbit, 2)*sin2m
	return toDegrees(equationOfTime) * 4
}

func getSunHourAngleAtSunriseSunset(lat, solarDec, zenith float64, sunrise bool) float64 {
	latRad, sdRad := toRadians(lat), toRadians(solarDec)
	result := math.Acos(math.Cos(toRadians(zenith))/(math.Cos(latRad)*math.Cos(sdRad)) - math.Tan(latRad)*math.Tan(sdRad)) //in radians
	if sunrise {
		return result
	}
	return -result
}

func getSunHourAngleAtSunrise(lat, solarDec, zenith float64) float64 {
	return getSunHourAngleAtSunriseSunset(lat, solarDec, zenith, true)
}

func getSunHourAngleAtSunset(lat, solarDec, zenith float64) float64 {
	return getSunHourAngleAtSunriseSunset(lat, solarDec, zenith, false)
}

func getSolarElevation(time time.Time, lat, lon float64) float64 {
	juliandDay := getJulianDay(time)
	julianCenturies := getJulianCenturiesFromJulianDay(juliandDay)
	eot := getEquationOfTime(julianCenturies)
	longitude := math.Mod(-((float64(time.Hour()) + 12 + (float64(time.Minute())+eot+float64(time.Second())/60)/60) * 15 /*360/24*/), 360)
	decRad := toRadians(getSunDeclination(julianCenturies))
	latRad := toRadians(lat)
	return toDegrees(math.Asin((math.Sin(latRad) * math.Sin(decRad)) + math.Cos(latRad)*math.Cos(decRad)*math.Cos(toRadians(lon-longitude))))
}

func getSolarAzimuth(time time.Time, lat, lon float64) float64 {
	juliandDay := getJulianDay(time)
	julianCenturies := getJulianCenturiesFromJulianDay(juliandDay)
	eot := getEquationOfTime(julianCenturies)
	longitude := math.Mod(-((float64(time.Hour()) + 12 + (float64(time.Minute())+eot+float64(time.Second())/60)/60) * 15 /*360/24*/), 360)
	hourAngleRad := toRadians(lon - longitude)
	decRad := toRadians(getSunDeclination(julianCenturies))
	latRad := toRadians(lat)
	return toDegrees(math.Atan(math.Sin(hourAngleRad)/((math.Cos(hourAngleRad)*math.Sin(latRad))-(math.Tan(decRad)*math.Cos(latRad))))) + 180
}

func getSolarNoonUTC(julianCenturies, longitude float64) float64 {
	tnoon := getJulianCenturiesFromJulianDay(getJulianDayFromJulianCenturies(julianCenturies) + longitude/360)
	eqTime := getEquationOfTime(tnoon)
	solNoonUTC := 720 + (longitude * 4) - eqTime
	newt := getJulianCenturiesFromJulianDay(getJulianDayFromJulianCenturies(julianCenturies) - 0.5 + solNoonUTC/1440)
	return 720 + (longitude * 4) - getEquationOfTime(newt)
}

func (c NOAACalculator) getTime(zenith float64, sunrise bool) time.Time {
	zenith = adjustZenith(zenith, c.Location.Elevation)
	julianDay := getJulianDay(c.Time)
	julianCenturies := getJulianCenturiesFromJulianDay(julianDay)
	// Find the time of solar noon at the location, and use that declination. This is better than start of the
	// Julian day

	noonmin := getSolarNoonUTC(julianCenturies, -c.Location.Lon)
	tnoon := getJulianCenturiesFromJulianDay(julianDay + noonmin/1440)

	// First calculates sunrise and approx length of day
	var hourAngle float64
	eqTime := getEquationOfTime(tnoon)
	solarDec := getSunDeclination(tnoon)
	if sunrise {
		hourAngle = getSunHourAngleAtSunrise(c.Location.Lat, solarDec, zenith)
	} else {
		hourAngle = getSunHourAngleAtSunset(c.Location.Lat, solarDec, zenith)
	}
	delta := -c.Location.Lon - toDegrees(hourAngle)
	timeDiff := 4 * delta
	timeUTC := 720 + timeDiff - eqTime

	// Second pass includes fractional Julian Day in gamma calc

	newt := getJulianCenturiesFromJulianDay(getJulianDayFromJulianCenturies(julianCenturies) + timeUTC/1440)
	eqTime = getEquationOfTime(newt)
	solarDec = getSunDeclination(newt)
	if sunrise {
		hourAngle = getSunHourAngleAtSunrise(c.Location.Lat, solarDec, zenith)
	} else {
		hourAngle = getSunHourAngleAtSunset(c.Location.Lat, solarDec, zenith)
	}
	delta = -c.Location.Lon - toDegrees(hourAngle)
	timeDiff = 4 * delta
	return getTimeFromFloat((720+timeDiff-eqTime)/60, c.Time) // in minutes
}

func adjustZenith(zenith, elevation float64) float64 {
	if zenith == geometricZenith {
		return zenith + solarRadius + refraction + toDegrees(math.Acos(earthRadius/(earthRadius+(elevation/1000))))
	}
	return zenith
}

func (c NOAACalculator) getCalculatorName() string {
	return "US National Oceanic and Atmospheric Administration Algorithm"
}

func (c NOAACalculator) Sunrise() time.Time {
	return c.getTime(geometricZenith, true)
}

func (c NOAACalculator) Sunset() time.Time {
	return c.getTime(geometricZenith, false)
}

func (c SunTimesCalculator) getTime(zenith float64, beforeNoon bool) time.Time {
	zenith = adjustZenith(zenith, c.Location.Elevation)
	var approx float64
	if beforeNoon {
		approx = float64(c.Time.YearDay()) + ((6 - (c.Location.Lon / 15)) / 24)
	} else {
		approx = float64(c.Time.YearDay()) + ((18 - (c.Location.Lon / 15)) / 24)
	}
	sunMeanAnomaly := (0.9856 * approx) - 3.289
	sunTrueLongitude := sunMeanAnomaly + (1.916 * math.Sin(toRadians(sunMeanAnomaly))) + (0.020 * math.Sin(toRadians(2*sunMeanAnomaly))) + 282.634
	if sunTrueLongitude >= 360 {
		sunTrueLongitude -= 360
	}
	if sunTrueLongitude < 0 {
		sunTrueLongitude += 360
	}
	rightAscensionHours := toDegrees(math.Atan(0.91764 * math.Tan(toRadians(sunTrueLongitude))))
	lQuadrant := math.Floor(sunTrueLongitude/90) * 90
	raQuadrant := math.Floor(rightAscensionHours/90) * 90
	rightAscensionHours = (rightAscensionHours + (lQuadrant - raQuadrant)) / 15 //15 = 360/24
	sinDec := 0.39782 * math.Sin(toRadians(sunTrueLongitude))
	cosLocalHourAngle := (math.Cos(toRadians(zenith)) - (sinDec * math.Sin(toRadians(c.Location.Lat)))) / (math.Cos(math.Asin(sinDec)) * math.Cos(toRadians(c.Location.Lat)))
	localHourAngle := toDegrees(math.Acos(cosLocalHourAngle))
	if beforeNoon {
		localHourAngle = 360 - localHourAngle
	}
	localMeanTime := ((localHourAngle / 15) + rightAscensionHours - (0.06571 * approx) - 6.622) - (c.Location.Lon / 15)
	for localMeanTime < 0 {
		localMeanTime += 24
	}
	for localMeanTime >= 24 {
		localMeanTime -= 24
	}
	return getTimeFromFloat(localMeanTime, c.Time)
}

func (c SunTimesCalculator) Sunrise() time.Time {
	return c.getTime(geometricZenith, true)
}

func (c SunTimesCalculator) Sunset() time.Time {
	return c.getTime(geometricZenith, false)
}
