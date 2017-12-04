"""
 * Zmanim Java API
 * Copyright (C) 2004-2011 Eliyahu Hershfeld
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
 * or connect to: http:#www.gnu.org/licenses/old-licenses/lgpl-2.1.html
"""
#package net.sourceforge.zmanim.util

#import java.util.Calendar
from datetime import datetime
import math
from utils import AstronomicalCalculator

"""*
 * Implementation of sunrise and sunset methods to calculate astronomical times based on the <a
 * href=""http:#noaa.gov">NOAA</a> algorithm. This calculator uses the Java algorithm based on the implementation by <a
 * href=""http:#noaa.gov">NOAA - National Oceanic and Atmospheric Administration</a>'s <a href =
 * "http:#www.srrb.noaa.gov/highlights/sunrise/sunrise.html">Surface Radiation Research Branch</a>. NOAA's <a
 * href="http:#www.srrb.noaa.gov/highlights/sunrise/solareqns.PDF">implementation</a> is based on equations from <a
 * href="http:#www.willbell.com/math/mc1.htm">Astronomical Algorithms</a> by <a
 * href="http:#en.wikipedia.org/wiki/Jean_Meeus">Jean Meeus</a>. Added to the algorithm is an adjustment of the zenith
 * to account for elevation. The algorithm can be found in the <a
 * href="http:#en.wikipedia.org/wiki/Sunrise_equation">Wikipedia Sunrise Equation</a> article.
 * 
 * @author &copy Eliyahu Hershfeld 2011
 * @version 0.1
"""
class NOAACalculator(AstronomicalCalculator):
    JULIAN_DAY_JAN_1_2000 = 2451545.0  # The Julian day of January 1 2000
    JULIAN_DAYS_PER_CENTURY = 36525.0  # Julian days per century


    def getCalculatorName(self):
        return "US National Oceanic and Atmospheric Administration Algorithm"

    def getUTCSunrise(self, dt, geoLocation, zenith, adjustForElevation):
        """See AstronomicalCalculator.getUTCSunrise"""
        if adjustForElevation:
            elevation = geoLocation.elevation
        else:
            elevation = 0
        adjustedZenith = self.adjustZenith(zenith, elevation)
        sunrise = self.getSunriseUTC(dt.toordinal(), geoLocation.latitude, -geoLocation.longitude,
                adjustedZenith)
        sunrise = sunrise / 60
        while (sunrise < 0.0):  # ensure that the time is >= 0 and < 24
            sunrise += 24.0
        while (sunrise >= 24.0):
            sunrise -= 24.0
        return sunrise

    def getUTCSunset(self, dt, geoLocation, zenith, adjustForElevation):
        """See AstronomicalCalculator.getUTCSunset"""
        if adjustForElevation:
            elevation = geoLocation.elevation
        else:
            elevation = 0
        adjustedZenith = self.adjustZenith(zenith, elevation)
        sunset = self.getSunsetUTC(dt.toordinal(), geoLocation.latitude, -geoLocation.longitude,
                adjustedZenith)
        sunset = sunset / 60
        while (sunset < 0.0):  # ensure that the time is >= 0 and < 24
            sunset += 24.0
        while (sunset >= 24.0):
            sunset -= 24.0
        return sunset

    def getJulianCenturiesFromJulianDay(self, julianDay):
        """Convert a Julian Day to centuries since J2000.0"""
        return (julianDay - self.JULIAN_DAY_JAN_1_2000) / self.JULIAN_DAYS_PER_CENTURY

    def getJulianDayFromJulianCenturies(self, julianCenturies):
        """Convert centuries since J2000.0 to a Julian Day"""
        return julianCenturies * self.JULIAN_DAYS_PER_CENTURY + self.JULIAN_DAY_JAN_1_2000

    def getSunGeometricMeanLongitude(self, julianCenturies):
        """Return the Geometric Mean Longitude of the Sun in degrees
        julianCenturies -- number of Julian centuries since J2000.0
        """
        longitude = 280.46646 + julianCenturies * (36000.76983 + 0.0003032 * julianCenturies)
        while (longitude > 360.0):
            longitude -= 360.0
        while (longitude < 0.0):
            longitude += 360.0
        return longitude # in degrees

    def getSunGeometricMeanAnomaly(self, julianCenturies):
        """Return the Geometric Mean Anomaly of the Sun in degrees
        julianCenturies -- number of Julian centuries since J2000.0
        """
        return 357.52911 + julianCenturies * (35999.05029 - 0.0001537 * julianCenturies) # in degrees

    def getEarthOrbitEccentricity(self, julianCenturies):
        """Return eccentricity of Earth's orbit (unitless)
        julianCenturies -- number of Julian centuries since J2000.0
        """
        return 0.016708634 - julianCenturies * (0.000042037 + 0.0000001267 * julianCenturies) # unitless

    def getSunEquationOfCenter(self, julianCenturies):
        """Return the equation of center for the Sun in degrees
        julianCenturies -- number of Julian centuries since J2000.0
        """
        m = self.getSunGeometricMeanAnomaly(julianCenturies)
        mrad = math.radians(m)
        sinm = math.sin(mrad)
        sin2m = math.sin(mrad + mrad)
        sin3m = math.sin(mrad + mrad + mrad)
        return (sinm * (1.914602 - julianCenturies * (0.004817 + 0.000014 * julianCenturies)) + sin2m
                * (0.019993 - 0.000101 * julianCenturies) + sin3m * 0.000289)  # in degrees

    def getSunTrueLongitude(self, julianCenturies):
        """Return the true longitude of the Sun in degrees
        julianCenturies -- number of Julian centuries since J2000.0
        """
        sunLongitude = self.getSunGeometricMeanLongitude(julianCenturies)
        center = self.getSunEquationOfCenter(julianCenturies)
        return sunLongitude + center # in degrees

    #def getSunTrueAnomaly(self, julianCenturies):
    #    """Return the true anamoly of the Sun in degrees
    #    julianCenturies -- number of Julian centuries since J2000.0
    #    """
    #    meanAnomaly = self.getSunGeometricMeanAnomaly(julianCenturies)
    #    equationOfCenter = self.getSunEquationOfCenter(julianCenturies)
    #    return meanAnomaly + equationOfCenter # in degrees

    def getSunApparentLongitude(self, julianCenturies):
        """Return the apparent longitude of the Sun in degrees
        julianCenturies -- number of Julian centuries since J2000.0
        """
        sunTrueLongitude = self.getSunTrueLongitude(julianCenturies)

        omega = 125.04 - 1934.136 * julianCenturies
        lambd = sunTrueLongitude - 0.00569 - 0.00478 * math.sin(math.radians(omega))
        return lambd # in degrees

    def getMeanObliquityOfEcliptic(self, julianCenturies):
        """Return the mean obliquity of the ecliptic (Axial Tilt) in degrees
        julianCenturies -- number of Julian centuries since J2000.0
        """
        seconds = (21.448 - julianCenturies
                * (46.8150 + julianCenturies
                * (0.00059 - julianCenturies
                * (0.001813))))
        return 23.0 + (26.0 + (seconds / 60.0)) / 60.0 # in degrees

    def getObliquityCorrection(self, julianCenturies):
        """Return the corrected obliquity of the ecliptic (Axial Tilt) in degrees
        julianCenturies -- number of Julian centuries since J2000.0
        """
        obliquityOfEcliptic = self.getMeanObliquityOfEcliptic(julianCenturies)

        omega = 125.04 - 1934.136 * julianCenturies
        return obliquityOfEcliptic + 0.00256 * math.cos(math.radians(omega)) # in degrees

    def getSunDeclination(self, julianCenturies):
        """Return the declination of the sun in degrees
        julianCenturies -- number of Julian centuries since J2000.0
        """
        obliquityCorrection = self.getObliquityCorrection(julianCenturies)
        lambd = self.getSunApparentLongitude(julianCenturies)

        sint = math.sin(math.radians(obliquityCorrection)) * math.sin(math.radians(lambd))
        theta = math.degrees(math.asin(sint))
        return theta # in degrees


    """*
     * Return the <a href="http:#en.wikipedia.org/wiki/Equation_of_time">Equation of Time</a> - the difference between
     * true solar time and mean solar time
     * 
     * @param julianCenturies
     *            the number of Julian centuries since J2000.0
     * @return equation of time in minutes of time
    """
    def getEquationOfTime(self, julianCenturies):
        """Return the Equation of Time (the difference between
        true solar time and mean solar time) in minutes
        julianCenturies -- number of Julian centuries since J2000.0
        """
        epsilon = self.getObliquityCorrection(julianCenturies)
        geomMeanLongSun = self.getSunGeometricMeanLongitude(julianCenturies)
        eccentricityEarthOrbit = self.getEarthOrbitEccentricity(julianCenturies)
        geomMeanAnomalySun = self.getSunGeometricMeanAnomaly(julianCenturies)
        y = math.tan(math.radians(epsilon) / 2.0)
        y = y*y
        sin2l0 = math.sin(2.0 * math.radians(geomMeanLongSun))
        sinm = math.sin(math.radians(geomMeanAnomalySun))
        cos2l0 = math.cos(2.0 * math.radians(geomMeanLongSun))
        sin4l0 = math.sin(4.0 * math.radians(geomMeanLongSun))
        sin2m = math.sin(2.0 * math.radians(geomMeanAnomalySun))
        equationOfTime = (y * sin2l0 - 2.0 * eccentricityEarthOrbit * sinm + 4.0 * eccentricityEarthOrbit * y
                * sinm * cos2l0 - 0.5 * y * y * sin4l0 - 1.25 * eccentricityEarthOrbit * eccentricityEarthOrbit * sin2m)
        return math.degrees(equationOfTime) * 4.0 # in minutes of time

    def getSunHourAngleAtSunrise(self, latitude, solarDec, zenith):
        """Return the hour angle of the sun at sunrise for the latitude in radians

        Arguments:
        latitude -- the latitude of observer in degrees
        solarDec -- the declination angle of sun in degrees
        zenith -- in degrees
        """
        latRad = math.radians(latitude)
        sdRad = math.radians(solarDec)

        return (math.acos(math.cos(math.radians(zenith)) / (math.cos(latRad) * math.cos(sdRad)) - math.tan(latRad)
                * math.tan(sdRad))) # in radians

    def getSunHourAngleAtSunset(self, lat, solarDec, zenith):  #duplication of getSunHourAngleAtSunrise and should be merged
        """Return the hour angle of the sun at sunset for the latitude in radians

        Arguments:
        latitude -- the latitude of observer in degrees
        solarDec -- the declination angle of sun in degrees
        zenith -- in degrees
        """
        latRad = math.radians(lat)
        sdRad = math.radians(solarDec)

        hourAngle = (math.acos(math.cos(math.radians(zenith)) / (math.cos(latRad) * math.cos(sdRad))
                - math.tan(latRad) * math.tan(sdRad)))
        return -hourAngle # in radians

    def getSunriseUTC(self, julianDay, latitude, longitude, zenith):
        """Return the Universal Coordinated Time (UTC) of sunrise for the given
        day at the given location on earth. Returns in minutes from zero UTC

        Arguments:
        julianDay -- the Julian day
        latitude -- the latitude of observer in degrees
        longitude -- the longitude of observer in degrees
        zenith -- zenith
        """
        julianCenturies = self.getJulianCenturiesFromJulianDay(julianDay)

        # Find the time of solar noon at the location, and use that declination.
        # This is better than start of the Julian day

        noonmin = self.getSolarNoonUTC(julianCenturies, longitude)
        tnoon = self.getJulianCenturiesFromJulianDay(julianDay + noonmin / 1440.0)

        # First pass to approximate sunrise (using solar noon)

        eqTime = self.getEquationOfTime(tnoon)
        solarDec = self.getSunDeclination(tnoon)
        hourAngle = self.getSunHourAngleAtSunrise(latitude, solarDec, zenith)

        delta = longitude - math.degrees(hourAngle)
        timeDiff = 4 * delta # in minutes of time
        timeUTC = 720 + timeDiff - eqTime # in minutes

        # Second pass includes fractional Julian Day in gamma calc

        newt = self.getJulianCenturiesFromJulianDay(self.getJulianDayFromJulianCenturies(julianCenturies) + timeUTC
                / 1440.0)
        eqTime = self.getEquationOfTime(newt)
        solarDec = self.getSunDeclination(newt)
        hourAngle = self.getSunHourAngleAtSunrise(latitude, solarDec, zenith)
        delta = longitude - math.degrees(hourAngle)
        timeDiff = 4 * delta
        timeUTC = 720 + timeDiff - eqTime # in minutes
        return timeUTC

    def getSolarNoonUTC(self, julianCenturies, longitude):
        """Return the Universal Coordinated Time (UTC) of solar noon for the given
        day at the given location on earth. Returns in minutes from zero UTC

        Arguments:
        julianCenturies -- the number of Julian centuries since J2000.0
        longitude -- the longitude of observer in degrees]
        """
        # First pass uses approximate solar noon to calculate eqtime
        tnoon = self.getJulianCenturiesFromJulianDay(self.getJulianDayFromJulianCenturies(julianCenturies) + longitude
                / 360.0)
        eqTime = self.getEquationOfTime(tnoon)
        solNoonUTC = 720 + (longitude * 4) - eqTime # min

        newt = self.getJulianCenturiesFromJulianDay(self.getJulianDayFromJulianCenturies(julianCenturies) - 0.5
                + solNoonUTC / 1440.0)

        eqTime = self.getEquationOfTime(newt)
        return 720 + (longitude * 4) - eqTime # min

    def getSunsetUTC(self, julianDay, latitude, longitude, zenith): # seems exactly the same as getSunriseUTS
        """Return the Universal Coordinated Time (UTC) of sunset for the given
        day at the given location on earth. Returns in minutes from zero UTC

        Arguments:
        julianDay -- the Julian day
        latitude -- the latitude of observer in degrees
        longitude -- the longitude of observer in degrees
        zenith -- zenith
        """
        julianCenturies = self.getJulianCenturiesFromJulianDay(julianDay)

        # Find the time of solar noon at the location, and use that declination. This is better than start of the
        # Julian day

        noonmin = self.getSolarNoonUTC(julianCenturies, longitude)
        tnoon = self.getJulianCenturiesFromJulianDay(julianDay + noonmin / 1440.0)

        # First calculates sunrise and approx length of day

        eqTime = self.getEquationOfTime(tnoon)
        solarDec = self.getSunDeclination(tnoon)
        hourAngle = self.getSunHourAngleAtSunset(latitude, solarDec, zenith)

        delta = longitude - math.degrees(hourAngle)
        timeDiff = 4 * delta
        timeUTC = 720 + timeDiff - eqTime

        # Second pass includes fractional Julian Day in gamma calc

        newt = self.getJulianCenturiesFromJulianDay(self.getJulianDayFromJulianCenturies(julianCenturies) + timeUTC
                / 1440.0)
        eqTime = self.getEquationOfTime(newt)
        solarDec = self.getSunDeclination(newt)
        hourAngle = self.getSunHourAngleAtSunset(latitude, solarDec, zenith)

        delta = longitude - math.degrees(hourAngle)
        timeDiff = 4 * delta
        timeUTC = 720 + timeDiff - eqTime # in minutes
        return timeUTC

        
