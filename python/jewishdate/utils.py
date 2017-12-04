"""
 * Zmanim Java API
 * Copyright (C) 2004-2013 Eliyahu Hershfeld
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
 * or connect to: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
"""

import abc
from pytz import timezone
import math
from datetime import datetime

class AstronomicalCalculator():
    """ An abstract class that all sun time calculating classes extend. This allows the algorithm used to be changed at
    runtime, easily allowing comparison the results of using different algorithms.
    """

    REFRACTION = 34.0 / 60.0  # The commonly used average solar refraction.
    #REFRACTION = 34.478885263888294 / 60.0  # Calendrical Calculations lists a more accurate global average of 34.478885263888294

    SOLAR_RADIUS = 16.0 / 60.0  # The commonly used average solar radius in minutes of a degree.
    EARTH_RADIUS = 6356.9 # Average in KM. Currently only affects elevation adjustment, not the sunrise/sunset calculations
    GEOMETRIC_ZENITH = 90  # The zenith of astronomical sunrise and sunset
    calculatorName = None # will be added in the subclasses

    def getDefault(self):
        """Sets SunTimesCalculator() as the default class for calculating sunrise and sunset."""
        return SunTimesCalculator()

    @abc.abstractmethod
    def getUTCSunrise(self, calendar, geoLocation, zenith, adjustForElevation):
        """ A method that calculates UTC sunrise as well as any time based on an angle above or below sunrise. This abstract
        method is implemented by the classes that extend this class.
        Return the UTC time of sunrise in 24 hour format. 5:45:00 AM will return 5.75.0. If an error was encountered in
        the calculation (expected behavior for some locations such as near the poles, None will be returned.
        
        calendar -- datetime object used to calculate day of year.
        geoLocation -- The location information used for astronomical calculating sun times. (A GeoLocation object)
        zenith -- the azimuth below the vertical zenith of 90 degrees. for sunrise typically the zenith used for the
        calculation uses geometric zenith of 90deg and method adjustZenith adjusts this slightly to account for
        solar refraction and the sun's radius.
        """
        return

    @abc.abstractmethod
    def getUTCSunset(self, calendar, geoLocation, zenith, adjustForElevation):
        """ A method that calculates UTC sunset as well as any time based on an angle above or below sunrise. This abstract
        method is implemented by the classes that extend this class.
        Return the UTC time of sunrise in 24 hour format. 5:45:00 AM will return 5.75.0. If an error was encountered in
        the calculation (expected behavior for some locations such as near the poles, None will be returned.
        
        calendar -- datetime object used to calculate day of year.
        geoLocation -- GeoLocation object of location information used for astronomical calculating sun times.
        zenith -- the azimuth below the vertical zenith of 90 degrees. for sunrise typically the zenith used for the
        calculation uses geometric zenith of 90deg and method adjustZenith adjusts this slightly to account for
        solar refraction and the sun's radius.
        """
        return

    def getElevationAdjustment(self, elevation):
        """Return the adjustment to the zenith required to account for the elevation. Since a person at a higher
        elevation can see farther below the horizon, the calculation for sunrise / sunset is calculated below the horizon
        used at sea level. This is only used for sunrise and sunset and not times before or after it such as
        AstronomicalCalendar.getBeginNauticalTwilight() since those calculations are based on the level of available
        light at the given dip below the horizon, something that is not affected by elevation, the adjustment should
        only made if the zenith == 90deg adjusted for refraction and solar radius.

        The algorithm used is:
        elevationAdjustment = math.toDegrees(math.acos(EARTH_RADIUSInMeters / (EARTH_RADIUSInMeters + elevationMeters)))
        
        The source of this algorthitm is <a href="http://www.calendarists.com">Calendrical Calculations</a> by Edward M.
        Reingold and Nachum Dershowitz. An alternate algorithm that produces an almost identical (but not accurate)
        result found in Ma'aglay Tzedek by Moishe Kosower and other sources is:
        
        elevationAdjustment = 0.0347 * math.sqrt(elevationMeters)
        
        Arguments:
        elevation -- elevation in Meters.
        """
        # double elevationAdjustment = 0.0347 * math.sqrt(elevation)
        return math.degrees(math.acos(self.EARTH_RADIUS / (self.EARTH_RADIUS + (elevation / 1000))))

    def adjustZenith(self, zenith, elevation):
        """Adjusts the zenith of astronomical sunrise and sunset to account for solar refraction, solar radius and
        elevation. The value for Sun's zenith and true rise/set Zenith (used in this class and subclasses) is the angle
        that the center of the Sun makes to a line perpendicular to the Earth's surface. If the Sun were a point and the
        Earth were without an atmosphere, true sunset and sunrise would correspond to a 90deg zenith. Because the Sun
        is not a point, and because the atmosphere refracts light, this 90deg zenith does not, in fact, correspond to
        true sunset or sunrise, instead the centre of the Sun's disk must lie just below the horizon for the upper edge
        to be obscured. This means that a zenith of just above 90deg must be used. The Sun subtends an angle of 16
        minutes of arc (SOLAR_RADIUS value), and atmospheric refraction accounts for 34 minutes or so (REFRACTION value),
        giving a total of 50 arcminutes. The total value for ZENITH is 90+(5/6) or 90.8333333deg for true sunrise/sunset.
        Since a person at an elevation can see blow the horizon of a person at sea level, this will also adjust the zenith
        to account for elevation if available. The zenith will only be adjusted for sunrise/sunset.
        
        Arguments:
        zenith -- degrees (eg 90.34)
        elevation -- in meters
        """
        if (zenith == self.GEOMETRIC_ZENITH): # only adjust if it is exactly sunrise or sunset
            return zenith + (self.SOLAR_RADIUS + self.REFRACTION + self.getElevationAdjustment(elevation))
        return zenith

class SunTimesCalculator(AstronomicalCalculator):
    """Implementation of sunrise and sunset methods to calculate astronomical times. This calculator uses the Java algorithm
    written by <a href="http://web.archive.org/web/20090531215353/http://www.kevinboone.com/suntimes.html">Kevin
    Boone</a> that is based on the <a href = "http://aa.usno.navy.mil/">US Naval Observatory's</a><a
    href="http://aa.usno.navy.mil/publications/docs/asa.php">Almanac</a> for Computer algorithm ( <a
    href="http://www.amazon.com/exec/obidos/tg/detail/-/0160515106/">Amazon</a>, <a
    href="http://search.barnesandnoble.com/booksearch/isbnInquiry.asp?isbn=0160515106">Barnes &amp Noble</a>) and is
    used with his permission. Added to Kevin's code is adjustment of the zenith to account for elevation.
    """

    calculatorName = "US Naval Almanac Algorithm"
    DEG_PER_HOUR = 360.0 / 24.0  # The number of degrees of longitude that corresponds to one hour time difference.

    def getUTCSunrise(self, calendar, geoLocation, zenith, adjustForElevation):
        """See AstronomicalCalculator.getUTCSunrise()"""
        if adjustForElevation:
            elevation = geoLocation.elevation
        else:
            elevation = 0
        adjustedZenith = self.adjustZenith(zenith, elevation)
        doubleTime = self.getTimeUTC(calendar.year, calendar.month,
                calendar.day, geoLocation.longitude, geoLocation.latitude,
                adjustedZenith, True)
        return doubleTime

    def getUTCSunset(self, calendar, geoLocation, zenith, adjustForElevation):
        """See AstronomicalCalculator.getUTCSunset()"""
        if adjustForElevation:
            elevation = geoLocation.elevation
        else:
            elevation = 0
        adjustedZenith = self.adjustZenith(zenith, elevation)

        doubleTime = self.getTimeUTC(calendar.year, calendar.month,
                calendar.day, geoLocation.longitude, geoLocation.latitude,
                adjustedZenith, False)
        return doubleTime

    def getDayOfYear(self, year, month, day):
        """Calculate the day of the year, where Jan 1st is day 1. Leap years have an impact here"""
        return datetime(year,month,day).timetuple().tm_yday

    def getHoursFromMeridian(self, longitude):
        """Return time difference between location's longitude and the Meridian, in hours. West of Meridian has a negative time
        difference
        """
        return longitude / self.DEG_PER_HOUR

    def getApproxTimeDays(self, dayOfYear, hoursFromMeridian, isSunrise):
        """Return the approximate time of sunset/sunrise in days since midnight Jan 1st, assuming 6am and 6pm events. We
        need this figure to derive the Sun's mean anomaly
        """
        if isSunrise:
            return dayOfYear + ((6.0 - hoursFromMeridian) / 24)
        else: # sunset
            return dayOfYear + ((18.0 - hoursFromMeridian) / 24)
    
    def getMeanAnomaly(self, dayOfYear, longitude, isSunrise):
        """Calculate the Sun's mean anomaly in degrees, at sunrise or sunset, given the longitude in degrees"""
        return (0.9856 * self.getApproxTimeDays(dayOfYear, self.getHoursFromMeridian(longitude), isSunrise)) - 3.289

    def getSunTrueLongitude(self, sunMeanAnomaly):
        """Calculates the Sun's true longitude in degrees. The result is an angle between 0 and 360. Requires the Sun's mean
        anomaly, also in degrees
        """
        sma_radians = math.radians(sunMeanAnomaly)
        l = sunMeanAnomaly + (1.916 * math.sin(sma_radians)) + (0.020 * math.sin(2 * sma_radians)) + 282.634
        while l >= 360.0: # get longitude into 0-360 degree range
            l -= 360.0
        while l < 0:
            l += 360.0
        return l

    def getSunRightAscensionHours(self, sunTrueLongitude):
        """Calculates the Sun's right ascension in hours, given the Sun's true longitude in degrees. Input and output are
        angles between 0 and 360.
        """
        a = 0.91764 * math.tan(math.radians(sunTrueLongitude))
        ra = math.degrees(math.atan(a))
        lQuadrant = math.floor(sunTrueLongitude / 90.0) * 90.0
        raQuadrant = math.floor(ra / 90.0) * 90.0
        ra = ra + (lQuadrant - raQuadrant)

        return ra / self.DEG_PER_HOUR # convert to hours

    def getCosLocalHourAngle(self, sunTrueLongitude, latitude, zenith):
        """Return the cosine of the Sun's local hour angle"""
        sinDec = 0.39782 * math.sin(math.radians(sunTrueLongitude))
        cosDec = math.cos(math.asin(sinDec))
        return (math.cos(math.radians(zenith)) - (sinDec * math.sin(math.radians(latitude)))) / (cosDec * math.cos(math.radians(latitude)))

    def getLocalMeanTime(self, localHour, sunRightAscensionHours, approxTimeDays):
        """Calculate local mean time of rising or setting. By `local' is meant the exact time at the location, assuming that
        there were no time zone. That is, the time difference between the location and the Meridian depended entirely on
        the longitude. We can't do anything with this time directly we must convert it to UTC and then to a local time.
        The result is expressed as a fractional number of hours since midnight
        """
        return localHour + sunRightAscensionHours - (0.06571 * approxTimeDays) - 6.622

    def getTimeUTC(self, year, month, day, longitude, latitude, zenith, isSunrise):
        """Get sunrise or sunset time in UTC, according to flag. Return a float (eg 9.4576) to be
        converted by AstronomicalCalendar.getDateFromTime()
        If an error was encountered in the calculation (expected behavior for some locations
        such as near the poles, None will be returned.

        Arguments:
        year --  4-digit year
        month --  1-12
        day --  1-31
        longitude --  in degrees, longitudes west of Meridian are negative (eg 40.005)
        latitude --  in degrees, latitudes south of equator are negative (eg -35.9087
        zenith --  Sun's zenith, in degrees (eg 90.833)
        isSunrise -- flag for sunrise(True) and Sunset(False)
        """
        dayOfYear = self.getDayOfYear(year, month, day)
        sunMeanAnomaly = self.getMeanAnomaly(dayOfYear, longitude, isSunrise)
        sunTrueLong = self.getSunTrueLongitude(sunMeanAnomaly)
        sunRightAscensionHours = self.getSunRightAscensionHours(sunTrueLong)
        cosLocalHourAngle = self.getCosLocalHourAngle(sunTrueLong, latitude, zenith)
        if (isSunrise):
            localHourAngle = 360.0 - math.degrees(math.acos(cosLocalHourAngle))
        else: # sunset
            localHourAngle = math.degrees(math.acos(cosLocalHourAngle))

        localHour = localHourAngle / self.DEG_PER_HOUR
        localMeanTime = self.getLocalMeanTime(localHour, sunRightAscensionHours,
                self.getApproxTimeDays(dayOfYear, self.getHoursFromMeridian(longitude), isSunrise))
        pocessedTime = localMeanTime - self.getHoursFromMeridian(longitude)
        while (pocessedTime < 0.0):
            pocessedTime += 24.0
        while (pocessedTime >= 24.0):
            pocessedTime -= 24.0
        return pocessedTime

class Time():
    """
    A class that represents a numeric time of temporal hour (Shaa Zmanis). Times that represent a time of day are stored as datetime in
    this API. The time class is used to represent numeric time such as the time in hours, minutes, seconds and
    milliseconds of temporal hour (Shaa Zmanis).
    Version 0.9.0
    """
    SECOND_MILLIS = 1000
    MINUTE_MILLIS = SECOND_MILLIS * 60
    HOUR_MILLIS = MINUTE_MILLIS * 60
    hours = 0
    minutes = 0
    seconds = 0
    milliseconds = 0
    isNegative = False

    def __init__(hours, minutes=None, seconds=None, milliseconds=None):
        if minutes == None:
            adjustedMillis = millis
            if (adjustedMillis < 0):
                this.isNegative = True
                adjustedMillis = abs(adjustedMillis)
            self.hours, adjustedMillis = divmod(adjustedMillis, self.HOUR_MILLIS)
            self.minutes, adjustedMillis = divmod(adjustedMillis,self.MINUTE_MILLIS)
            self.seconds, self.milliseconds = divmod(adjustedMillis,self.SECOND_MILLIS)
        else:
            self.hours = hours
            self.minutes = minutes
            self.seconds = seconds
            self.milliseconds = milliseconds


    def isNegative(self):
        return self.isNegative

    def setIsNegative(self, isNegative):
        self.isNegative = isNegative


    def getTime(self):
        return self.hours * self.HOUR_MILLIS + self.minutes * self.MINUTE_MILLIS + self.seconds * self.SECOND_MILLIS + self.milliseconds


class GeoLocationUtils():
    """A class for various location calculations
    Most of the code in this class is ported from <a href="http://www.movable-type.co.uk/">Chris Veness'</a>
    <a href="http://www.fsf.org/licensing/licenses/lgpl.html">LGPL</a> Javascript Implementation
    Author: Eliyahu Hershfeld 2009
    Version: 0.1
    """
    DISTANCE = 0
    INITIAL_BEARING = 1
    FINAL_BEARING = 2

    def getGeodesicInitialBearing(location, destination):
        """Calculate the initial <a href="http://en.wikipedia.org/wiki/Great_circle">geodesic</a> bearing
        between two objects passed to this method using <a href="http://en.wikipedia.org/wiki/Thaddeus_Vincenty">
        Thaddeus Vincenty's</a> inverse formula See T Vincenty, "<a href="http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf">
        Direct and Inverse Solutions of Geodesics on the Ellipsoid with application of nested
        equations</a>", Survey Review, vol XXII no 176, 1975.

        Arguments:
        location -- a GeoLocation of the starting location
        destination -- a GeoLocation of the destination
        """
        return self.vincentyFormula(location, destination, self.INITIAL_BEARING)

    """*
     * Calculate the final <a
     * href="http://en.wikipedia.org/wiki/Great_circle">geodesic</a> bearing
     * between this Object and a second Object passed to this method using <a
     * href="http://en.wikipedia.org/wiki/Thaddeus_Vincenty">Thaddeus Vincenty's</a>
     * inverse formula See T Vincenty, "<a
     * href="http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf">Direct and Inverse
     * Solutions of Geodesics on the Ellipsoid with application of nested
     * equations</a>", Survey Review, vol XXII no 176, 1975.
     *
     * @param location
     *            the destination location
    """
    def getGeodesicFinalBearing(location, destination):
        """Calculate the Final <a href="http://en.wikipedia.org/wiki/Great_circle">geodesic</a> bearing
        between two objects passed to this method using <a href="http://en.wikipedia.org/wiki/Thaddeus_Vincenty">
        Thaddeus Vincenty's</a> inverse formula See T Vincenty, "<a href="http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf">
        Direct and Inverse Solutions of Geodesics on the Ellipsoid with application of nested
        equations</a>", Survey Review, vol XXII no 176, 1975.

        Arguments:
        location -- a GeoLocation of the starting location
        destination -- a GeoLocation of the destination
        """
        return self.vincentyFormula(location, destination, self.FINAL_BEARING)

    def getGeodesicDistance(location, destination):
        """Calculate <a href="http://en.wikipedia.org/wiki/Great_circle">geodesic distance</a>
        between two objects passed to this method using <a href="http://en.wikipedia.org/wiki/Thaddeus_Vincenty">
        Thaddeus Vincenty's</a> inverse formula See T Vincenty, "<a href="http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf">
        Direct and Inverse Solutions of Geodesics on the Ellipsoid with application of nested
        equations</a>", Survey Review, vol XXII no 176, 1975.

        Arguments:
        location -- a GeoLocation of the starting location
        destination -- a GeoLocation of the destination
        """
        return self.vincentyFormula(location, destination, self.DISTANCE)

    def vincentyFormula(self, location, destination, formula):
        """Calculate the <a href="http://en.wikipedia.org/wiki/Great_circle">geodesic distance </a>
        between two objects passed to this method using <a href="http://en.wikipedia.org/wiki/Thaddeus_Vincenty">
        Thaddeus Vincenty's</a> inverse formula See T Vincenty, "<a href="http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf">
        Direct and Inverse Solutions of Geodesics on the Ellipsoid with application of nested
        equations</a>", Survey Review, vol XXII no 176, 1975.

        Arguments:
        location -- a GeoLocation of the starting location
        destination -- a GeoLocation of the destination
        formula -- the formula to use - self.DISTANCE, self.FINAL_BEARING or self.INITIAL_BEARING
        """
        a = 6378137
        b = 6356752.3142
        f = 1 / 298.257223563 # WGS-84 ellipsiod
        L = math.radians(destination.longitude - location.longitude)
        U1 = math.atan((1 - f) * math.tan(math.radians(location.latitude)))
        U2 = math.atan((1 - f) * math.tan(math.radians(location.latitude)))
        sinU1 = math.sin(U1)
        cosU1 = math.cos(U1)
        sinU2 = math.sin(U2)
        cosU2 = math.cos(U2)

        lambdaA = L
        lambdaP = 2 * math.pi
        iterLimit = 20
        sinLambda = 0
        cosLambda = 0
        sinSigma = 0
        cosSigma = 0
        sigma = 0
        sinAlpha = 0
        cosSqAlpha = 0
        cos2SigmaM = 0
        C = 0
        while ((math.fabs(lambdaA - lambdaP) > 1e-12) and (iterLimit > 0)):
            iterLimit -= 1
            sinLambda = math.sin(lambdaA)
            cosLambda = math.cos(lambdaA)
            sinSigma = math.sqrt((cosU2 * sinLambda) * (cosU2 * sinLambda)
                    + (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) * (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda))
            if (sinSigma == 0):
                return 0 # co-incident points
            cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
            sigma = math.atan2(sinSigma, cosSigma)
            sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
            cosSqAlpha = 1 - sinAlpha * sinAlpha
            cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha
            if (math.isnan(cos2SigmaM)):
                cos2SigmaM = 0 # equatorial line: cosSqAlpha=0 
            C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
            lambdaP = lambdaA
            lambdaA = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)))
    
        if (iterLimit == 0):
            return None # formula failed to converge

        uSq = cosSqAlpha * (a * a - b * b) / (b * b)
        A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
        B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
        deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM) - B / 6 * cos2SigmaM * (-3 + 4 * sinSigma * sinSigma) * (-3 + 4 * cos2SigmaM * cos2SigmaM)))
        distance = b * A * (sigma - deltaSigma)

        # initial bearing
        fwdAz = math.degrees(math.atan2(cosU2 * sinLambda, cosU1 * sinU2 - sinU1 * cosU2 * cosLambda))
        # final bearing
        revAz = math.degrees(math.atan2(cosU1 * sinLambda, -sinU1 * cosU2 + cosU1 * sinU2 * cosLambda))
        if (formula == self.DISTANCE):
            return distance
        elif (formula == self.INITIAL_BEARING):
            return fwdAz
        elif (formula == self.FINAL_BEARING):
            return revAz
        else: # should never happpen
            return None

    def getRhumbLineBearing(self, location, destination):
        """Returns the <a href="http://en.wikipedia.org/wiki/Rhumb_line">rhumb line</a>
        bearing in degrees from the starting location to the GeoLocation passed in.

        Arguments:
        location -- a GeoLocation of the starting location
        destination -- a GeoLocation of the destination
        """
        dLon = math.radians(destination.longitude - location.longitude)
        dPhi = math.log(math.tan(math.radians(destination.latitude) / 2 + math.pi / 4)
                / math.tan(math.radians(location.latitude) / 2 + math.pi / 4))
        if (math.fabs(dLon) > math.pi):
            if dLon > 0:
                dLon = -(2 * math.pi - dLon)
            else:
                dLon = (2 * math.pi + dLon)
        return math.degrees(math.atan2(dLon, dPhi))

    def getRhumbLineDistance(self, location, destination):
        """Returns the <a href="http://en.wikipedia.org/wiki/Rhumb_line">rhumb line</a>
        distance in meters from the starting location to the GeoLocation passed in.

        Arguments:
        location -- a GeoLocation of the starting location
        destination -- a GeoLocation of the destination
        """
        R = 6371 # earth's mean radius in km
        dLat = math.radians(destination.latitude - location.latitude)
        dLon = math.radians(math.fabs(destination.longitude - location.longitude))
        dPhi = math.log(math.tan(math.radians(destination.longitude) / 2 + math.pi / 4)
                / math.tan(math.radians(location.latitude) / 2 + math.pi / 4))
        if (math.fabs(dLat) > 1e-10):
            q = dLat / dPhi
        else:
            q = math.cos(math.toRadians(location.latitude))
        # if dLon over 180degrees take shorter rhumb across 180degrees meridian:
        if (dLon > math.pi):
            dLon = 2 * math.pi - dLon
        d = math.sqrt(dLat * dLat + q * q * dLon * dLon)
        return d * R

class GeoLocation(GeoLocationUtils):
    """A class that contains location information such as latitude and longitude required for astronomical calculations. The
    elevation field may not be used by some calculation engines and would be ignored if set. Check the documentation for
    specific implementations of the AstronomicalCalculator to see if elevation is calculated as part of the
    algorithm.
    
    Author: Eliyahu Hershfeld 2004 - 2012
    Version: 1.1
    """
    DISTANCE = 0
    INITIAL_BEARING = 1
    FINAL_BEARING = 2
    MINUTE_MILLIS = 60 * 1000  # constant for milliseconds in a minute (60,000)
    HOUR_MILLIS = MINUTE_MILLIS * 60  # constant for milliseconds in an hour (3,600,000)

    @property
    def elevation(self):
        """Elevation in Meters."""
        return self._elevation

    @elevation.setter
    def elevation(self, elevation):
        """Method to set the elevation in Meters above sea level."""
        if (elevation < 0):
            raise IllegalArgumentException("Elevation cannot be negative")
        self._elevation = elevation

    def __init__(self, name="Greenwich, England", latitude=51.4772, longitude=0, elevation=0, tz=timezone("Etc/GMT")):
        """GeoLocation constructor with parameters for all required fields.
        
        Keyword Arguments:
        name -- The location name for display use (Default "Greenwich, England")
        latitude -- the latitude in a format such as 40.095965 for Lakewood, NJ (Default 51.4772)
        Note: For latitudes south of the equator, a negative value should be used.
        longitude -- the longitude in a format such as -74.222130 for Lakewood, NJ.  (Default 0)
        Note: For longitudes east of the <a href="http://en.wikipedia.org/wiki/Prime_Meridian">Prime
        Meridian </a> (Greenwich), a negative value should be used.
        elevation -- the elevation above sea level in Meters. Elevation is not used in most algorithms used for calculating
        sunrise and set.
        tz -- the TimeZone for the location. (Default timezone("Etc/GMT"))
        """
        self.locationName = name
        self.setLatitude(latitude)
        self.setLongitude(longitude)
        if type(elevation) is int:
            self._elevation = elevation
            self.timeZone = tz 
        else:
            try:
                elevation.zone
                self._elevation = 0
                self.timeZone = elevation
            except:
                pass

    def setLatitude(self, degrees, minutes=None, seconds=None, direction=None):
        """Method to set the latitude.
        2 types of arguments:
        latitude -- The degrees of latitude to set. The values should be between -90deg and 90deg. An 
        IllegalArgumentException will be thrown if the value exceeds the limit. For example 40.095965 would be
        used for Lakewood, NJ.
        Note: For latitudes south of the equator, a negative value should beused.
        
        Otherwise latitude can be set in degrees, minutes and seconds.
        Arguments:
        degrees -- The degrees of latitude to set between -90 and 90. An IllegalArgumentException will be thrown if the
        value exceeds the limit. For example 40 would be used for Lakewood, NJ.
        minutes -- <a href="http://en.wikipedia.org/wiki/Minute_of_arc#Cartography">minutes of arc</a>
        seconds -- <a href="http://en.wikipedia.org/wiki/Minute_of_arc#Cartography">seconds of arc</a>
        direction -- N for north and S for south. An IllegalArgumentException will be thrown if the value is not S or N.
        """
        if (isinstance(degrees, float)) and (minutes == None):
            if (degrees > 90 or degrees < -90):
                raise IllegalArgumentException("Latitude must be between -90 and  90")
            self._latitude = degrees
        elif (isinstance(degrees, int)) and (isinstance(seconds, int)):
            tempLat = degrees + ((minutes + (seconds / 60.0)) / 60.0)
            if (tempLat > 90 or tempLat < 0):
                raise IllegalArgumentException(
                        "Latitude must be between 0 and  90. Use direction of S instead of negative.")
        
            if (direction == "S"):
                tempLat *= -1
            elif (not (direction == "N")):
                raise IllegalArgumentException("Latitude direction must be N or S")
        
            self._latitude = tempLat

    def setLongitude(self, degrees, minutes=None, seconds=None, direction=None):
        """Method to set the longitude.
        2 types of arguments:
        latitude -- The degrees of longitude to set. The values should be between -180deg and 1800deg. An 
        IllegalArgumentException will be thrown if the value exceeds the limit. For example -74.2094 would be
        used for Lakewood, NJ.
        Note: for longitudes east of the <a href="http://en.wikipedia.org/wiki/Prime_Meridian">
        Prime Meridian</a> (Greenwich), a negative value should be used.
        
        Otherwise longitude can be set in degrees, minutes and seconds.
        Arguments:
        degrees -- The degrees of longitude to set between -180 and 180. An IllegalArgumentException will be thrown if the
        value exceeds the limit. For example -74 would be used for Lakewood, NJ.
        Note: for longitudes east of the <a href="http://en.wikipedia.org/wiki/Prime_Meridian">
        Prime Meridian</a> (Greenwich), a negative value should be used.
        minutes -- <a href="http://en.wikipedia.org/wiki/Minute_of_arc#Cartography">minutes of arc</a>
        seconds -- <a href="http://en.wikipedia.org/wiki/Minute_of_arc#Cartography">seconds of arc</a>
        direction -- E for East and W for West. An IllegalArgumentException will be thrown if the value is not E or W.
        """
        if (isinstance(degrees, float)) and (minutes == None):
            if (degrees > 180 or degrees < -180):
                raise IllegalArgumentException("Longitude must be between -180 and  180")
            self._longitude = degrees
        elif (isinstance(degrees, int)) and (isinstance(seconds, int)):
            longTemp = degrees + ((minutes + (seconds / 60.0)) / 60.0)
            if (longTemp > 180 or self.longitude < 0):
                raise IllegalArgumentException("Longitude must be between 0 and  180.")
            if (direction == "W"):
                longTemp *= -1
            elif (not (direction == "E")):
                raise IllegalArgumentException("Longitude direction must be E or W")
        
            self._longitude = longTemp

    @property
    def longitude(self):
        """Latitude"""
        return self._longitude

    @property
    def latitude(self):
        """Latitude"""
        return self._latitude

    def getLocalMeanTimeOffset(self):
        """Return the offset in milliseconds not accounting for Daylight saving time. A positive value will be returned
        East of the 15deg timezone line, and a negative value West of it.

        A method that will return the location's local mean time offset in milliseconds from local <a
        href="http://en.wikipedia.org/wiki/Standard_time">standard time</a>. The globe is split into 360deg, with
        15deg per hour of the day. For a local that is at a longitude that is evenly divisible by 15 (longitude % 15 ==
        0), at solar noon AstronomicalCalendar.getSunTransit() (with adjustment for the <a
        href="http://en.wikipedia.org/wiki/Equation_of_time">equation of time</a>) the sun should be directly overhead,
        so a user who is 1deg west of this will have noon at 4 minutes after standard time noon, and conversely, a user
        who is 1deg east of the 15deg longitude will have noon at 11:56 AM. Lakewood, N.J., whose longitude is
        -74.2094, is 0.7906 away from the closest multiple of 15 at -75deg. This is multiplied by 4 to yield 3 minutes
        and 10 seconds earlier than standard time. The offset returned does not account for the <a
        href="http://en.wikipedia.org/wiki/Daylight_saving_time">Daylight saving time</a> offset since this class is
        unaware of dates.
        """
        return self.longitude * 4 * self.MINUTE_MILLIS - (self.timeZone._utcoffset.total_seconds() *1000) # uses private variable

    def getGeodesicInitialBearing(self, location):
        """ Calculate the initial <a href="http://en.wikipedia.org/wiki/Great_circle">geodesic</a> bearing between this
        Object and a second Object passed to this method using <a
        href="http://en.wikipedia.org/wiki/Thaddeus_Vincenty">Thaddeus Vincenty's</a> inverse formula See T Vincenty, "<a
        href="http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf">Direct and Inverse Solutions of Geodesics on the Ellipsoid
        with application of nested equations</a>", Survey Review, vol XXII no 176, 1975
        
        Argumets:
        location -- the destination location
        """
        return GeoLocationUtils.vincentyFormula(self, location, self.INITIAL_BEARING)

    def getGeodesicFinalBearing(self, location):
        """ Calculate the final <a href="http://en.wikipedia.org/wiki/Great_circle">geodesic</a> bearing between this
        Object and a second Object passed to this method using <a
        href="http://en.wikipedia.org/wiki/Thaddeus_Vincenty">Thaddeus Vincenty's</a> inverse formula See T Vincenty, "<a
        href="http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf">Direct and Inverse Solutions of Geodesics on the Ellipsoid
        with application of nested equations</a>", Survey Review, vol XXII no 176, 1975
        
        Argumets:
        location -- the destination location
        """
        return GeoLocationUtils.vincentyFormula(self, location, self.FINAL_BEARING)

    def getGeodesicDistance(self, location):
        """ Calculate the <a href="http://en.wikipedia.org/wiki/Great_circle">geodesic distance</a> between this
        Object and a second Object passed to this method using <a
        href="http://en.wikipedia.org/wiki/Thaddeus_Vincenty">Thaddeus Vincenty's</a> inverse formula See T Vincenty, "<a
        href="http://www.ngs.noaa.gov/PUBS_LIB/inverse.pdf">Direct and Inverse Solutions of Geodesics on the Ellipsoid
        with application of nested equations</a>", Survey Review, vol XXII no 176, 1975
        
        Argumets:
        location -- the destination location
        """
        return GeoLocationUtils.vincentyFormula(self, location, self.DISTANCE)

    def vincentyFormula(self, destination, formula):
        return GeoLocationUtils.vincentyFormula(self, destination, formula) # passing self as 2nd argument in parent method

    def getRhumbLineBearing(self, destination):
        """Returns the <a href="http://en.wikipedia.org/wiki/Rhumb_line">rhumb line</a>
        bearing in degrees to the GeoLocation passed in.

        Arguments:
        destination -- a GeoLocation of the destination
        """
        return GeoLocationUtils.getRhumbLineBearing(self, destination)  # passing self as 2nd argument in parent method

    def getRhumbLineDistance(self, destination):
        """Returns the <a href="http://en.wikipedia.org/wiki/Rhumb_line">rhumb line</a>
        distance in meters to the GeoLocation passed in.

        Arguments:
        destination -- a GeoLocation of the destination
        """
        return GeoLocationUtils.getRhumbLineDistance(self, destination)  # passing self as 2nd argument in parent method

class ZmanimCalculator(AstronomicalCalculator):
    calculatorName = "US Naval Almanac Algorithm"

    def getCalculatorName():
        return self.calculatorName

    def getUTCSunrise(self, dt, geoLocation, zenith, adjustForElevation):
        """See AstronomicalCalculator.getUTCSunrise()"""
        return self.getUTCSunriseSunset(dt, geoLocation, zenith, adjustForElevation, True)

    def getUTCSunset(self, dt, geoLocation, zenith, adjustForElevation):
        """See AstronomicalCalculator.getUTCSunset()"""
        return self.getUTCSunriseSunset(dt, geoLocation, zenith, adjustForElevation, False)

    def getUTCSunriseSunset(self, dt, geoLocation, zenith, adjustForElevation, issunrise):
        """Get sunrise or sunset time in UTC, according to flag. Return a float (eg 9.4576) to be
        converted by AstronomicalCalendar.getDateFromTime()
        If an error was encountered in the calculation (expected behavior for some locations
        such as near the poles, None will be returned.

        Arguments:
        dt --  a datetime object
        geolocation -- a GeoLocation object
        zenith --  Sun's zenith, in degrees (eg 90.833)
        isSunrise -- flag for sunrise(True) and Sunset(False)
        """
        if adjustForElevation:
            elevation = geoLocation.elevation
        else:
            elevation = 0

        adjustedZenith = self.adjustZenith(zenith, elevation)

        # step 1: First calculate the day of the year
        #int N = calendar.get(Calendar.DAY_OF_YEAR)

        # step 2: convert the longitude to hour value and calculate an approximate time
        lngHour = geoLocation.longitude / 15

        if issunrise:
            a = 6
        else:
            a = 18

        t = dt.timetuple().tm_yday + ((a - lngHour) / 24) #is 6 in sunrise instead of 18

        # step 3: calculate the sun's mean anomaly
        M = (0.9856 * t) - 3.289

        # step 4: calculate the sun's true longitude
        L = M + (1.916 * math.sin(math.radians(M))) + (0.020 * math.sin(math.radians(2 * M))) + 282.634
        while (L < 0):
            L += 360
    
        while (L >= 360):
            L -= 360

        # step 5a: calculate the sun's right ascension
        RA = math.degrees(math.atan(0.91764 * math.tan(math.radians(L))))

        while (RA < 0):
            RA += 360
    
        while (RA >= 360):
            RA -= 360
    

        # step 5b: right ascension value needs to be in the same quadrant as L
        lQuadrant = math.floor(L / 90) * 90
        raQuadrant = math.floor(RA / 90) * 90
        RA = RA + (lQuadrant - raQuadrant)

        # step 5c: right ascension value needs to be converted into hours
        RA /= 15

        # step 6: calculate the sun's declination
        sinDec = 0.39782 * math.sin(math.radians(L))
        cosDec = math.cos(math.asin(sinDec))

        # step 7a: calculate the sun's local hour angle
        cosH = (math.cos(math.radians(adjustedZenith)) - (sinDec * math.sin(math.radians(geoLocation
                .latitude)))) / (cosDec * math.cos(math.radians(geoLocation.latitude)))

        # step 7b: finish calculating H and convert into hours
        if issunrise:
            H = 360 - math.degrees(math.acos(cosH))
        else:
            H = math.degrees(math.acos(cosH))

        H = H / 15.0

        # step 8: calculate local mean time

        T = H + RA - (0.06571 * t) - 6.622

        # step 9: convert to UTC
        UT = T - lngHour
        while (UT < 0):
            UT += 24
    
        while (UT >= 24):
            UT -= 24
    
        return UT
