"""
 * Zmanim Java API
 * Copyright (C) 2004-2012 Eliyahu Hershfeld
 *
 * This library is free software you can redistribute it and/or modify it under the terms of the GNU Lesser General
 * Public License as published by the Free Software Foundation either version 2.1 of the License, or (at your option)
 * any later version.
 *
 * This library is distributed in the hope that it will be useful,but WITHOUT ANY WARRANTY without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
 * details.
 * You should have received a copy of the GNU Lesser General Public License along with this library if not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA,
 * or connect to: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
 """
from datetime import datetime, timedelta

from pytz import timezone
from utils import GeoLocation, SunTimesCalculator, AstronomicalCalculator

class AstronomicalCalendar(AstronomicalCalculator):
    """A calendar that calculates astronomical times such as sunrise and sunset times. This class contains a
    datetime object and can therefore use the standard datetime functionality to change dates etc...
    The calculation engine used to calculate the astronomical times can be changed to a different implementation
    by modifying the astronomical_calculator property. A number of different calculation engine implementations
    are included in the util package.
    Note: There are times when the algorithms can't calculate proper values for sunrise, sunset and twilight. This
    is usually caused by trying to calculate times for areas either very far North or South, where sunrise / sunset never
    happen on that date. This is common when calculating twilight with a deep dip below the horizon for locations as far
    south of the North Pole as London, in the northern hemisphere. The sun never reaches this dip at certain times of the
    year. When the calculations encounter this condition a None value will be returned.

    Here is a simple example of how to use the API to calculate sunrise:
    First create the Calendar for the location you would like to calculate sunrise or sunset times for:
    location_name = "Lakewood, NJ"
    latitude = 40.0828 # Lakewood, NJ
    longitude = -74.2094 # Lakewood, NJ
    elevation = 20 # optional elevation correction in Meters
    tz = timezone("America/New_York")
    location = GeoLocation(location_name, latitude, longitude, elevation, tz)
    ac = AstronomicalCalendar(location)

    To get the time of sunrise, first set the date you want (if not set, the date will default to today):
    ac.dt = datetime(2012, 2, 8)
    sunrise = ac.getSunrise()

    Author: Eliyahu Hershfeld 2004 - 2012
    Version: 1.2.1
    """


    """Default value for Sun's zenith and true rise/set Zenith (used in this class and subclasses) is the angle that the
    center of the Sun makes to a line perpendicular to the Earth's surface. If the Sun were a point and the Earth
    were without an atmosphere, true sunset and sunrise would correspond to a 90 deg zenith. Because the Sun is not
    a point, and because the atmosphere refracts light, this 90 deg zenith does not, in fact, correspond to true
    sunset or sunrise, instead the center of the Sun's disk must lie just below the horizon for the upper edge to be
    obscured. This means that a zenith of just above 90 deg must be used. The Sun subtends an angle of 16 minutes of
    arc (this can be changed via the SUN_RADIUS property, and atmospheric refraction accounts for
    34 minutes or so (this can be changed via the REFRACTION property), giving a total of 50
    arcminutes. The total value for ZENITH is 90+(5/6) or 90.8333333 deg for true sunrise/sunset.
    """
    GEOMETRIC_ZENITH = 90  # Will be adjusted to account for radius of the sun and refraction
    #ZENITH = self.GEOMETRIC_ZENITH + 5.0 / 6.0
    CIVIL_ZENITH = 96  # Sun's zenith at civil twilight - 96 Deg
    NAUTICAL_ZENITH = 102  # Sun's zenith at nautical twilight - 102 Deg
    ASTRONOMICAL_ZENITH = 108  # Sun's zenith at astronomical twilight - 108 Deg

    _dt = None
    _geolocation = None
    _sunrise = None
    _sunset = None
    astronomical_calculator = None

    def getSunrise(self):
        """Return an elevation adjusted sunrise datetime or None when there is no sunrise"""
        sunrise = self.getUTCSunrise(self.GEOMETRIC_ZENITH)
        if not sunrise:
            return None
        else:
            return self.getDateFromTime(sunrise)

    def getSeaLevelSunrise(self):
        """Return an sunrise datetime not adjusted for elevation or None when there is no sunrise
        Non-sunrise and sunset calculations such as dawn and dusk, depend on the amount of visible light,
        something that is not affected by elevation. This method returns sunrise calculated at sea level. This
        forms the base for dawn calculations that are calculated as a dip below the horizon before sunrise.
        """
        sunrise = self.getUTCSeaLevelSunrise(self.GEOMETRIC_ZENITH)
        if not sunrise:
            return None
        else:
            return self.getDateFromTime(sunrise)

    def getBeginCivilTwilight():
        """Return datetime the beginning of civil twilight using a zenith of 96 deg"""
        return self.getSunriseOffsetByDegrees(self.CIVIL_ZENITH)

    def getBeginNauticalTwilight():
        """Return datetime the beginning of nautical twilight using a zenith of 102 deg"""
        return self.getSunriseOffsetByDegrees(self.NAUTICAL_ZENITH)

    def getBeginAstronomicalTwilight():
        """Return datetime the beginning of astronomical twilight using a zenith of 108 deg"""
        return self.getSunriseOffsetByDegrees(self.ASTRONOMICAL_ZENITH)

    def getSunset(self):
        """Return a datetime representing the elevation adjusted sunset time. The zenith used for
        the calculation uses geometric zenithof 90deg plus elevation adjustment. This is then adjusted to add
        approximately 50/60 of a degree to account for 34 archminutes of refraction and 16 archminutes for the
        sun's radius for a total of 90.83333 deg.

        See documentation for the specific implementation of the AstronomicalCalculator that you are using.
        
        Note:
        In certain cases the calculates sunset will occur before sunrise. This will typically happen when a timezone
        other than the local timezone is used (calculating Los Angeles sunset using a GMT timezone for example). In this
        case the sunset date will be incremented to the following date.
        """
        sunset = self.getUTCSunset(self.GEOMETRIC_ZENITH)
        if not sunset:
            return None
        else:
            return self.getAdjustedSunsetDate(self.getDateFromTime(sunset), self.getSunrise())

    def getAdjustedSunsetDate(self, sunset, sunrise):
        """A method that will roll the sunset time forward a day if sunset occurs before sunrise.
        This is a rare occurrence and will typically happen when calculating very early and late twilights 
        in a location with a time zone far off from its natural 15 deg boundaries. This method will ensure that
        in this case, the sunset will be incremented to the following date.
        An example of this is Marquette, Michigan that far west of the natural boundaries for EST. When you add
        in DST this pushes it an additional hour off. Calculating the extreme 26 deg twilight on March 6th
        it start at 2:34:30 on the 6th and end at 1:01:46 on the following day March 7th. Occurrences are more common in
        the polar region for dips as low as 3 deg (Tested for Hooper Bay, Alaska).

        TODO: Since the occurrences are rare, look for optimization to avoid relatively expensive calls to this method.
        """
        if (sunset and sunrise and sunrise > sunset):
            return sunset + timedelta(days=1)
        return sunset

    def getSeaLevelSunset(self):
        """Return an sunset datetime not adjusted for elevation or None when there is no sunset.

        Non-sunrise and sunset calculations, such as dawn and dusk, depend on the amount of visible light,
        something that is not affected by elevation. This method returns sunset calculated at sea level. This
        forms the base for dusk calculations that are calculated as a dip below the horizon after sunset.
        """
        sunset = self.getUTCSeaLevelSunset(self.GEOMETRIC_ZENITH)
        if not sunset:
            return None
        else:
            return self.getAdjustedSunsetDate(self.getDateFromTime(sunset), self.getSeaLevelSunrise())

    def getEndCivilTwilight(self):
        """Return the end of civil twilight using a zenith of CIVIL_ZENITH (96 Deg)"""
        return self.getSunsetOffsetByDegrees(self.CIVIL_ZENITH)

    def getEndNauticalTwilight(self):
        """Return the end of nautical twilight using a zenith of NAUTICAL_ZENITH (102 Deg)"""
        return self.getSunsetOffsetByDegrees(self.NAUTICAL_ZENITH)

    def getEndAstronomicalTwilight(self):
        """Return the end of astronomical twilight using a zenith of ASTRONOMICAL_ZENITH (108 Deg)"""
        return self.getSunsetOffsetByDegrees(self.ASTRONOMICAL_ZENITH)

    def getSunriseOffsetByDegrees(self, offsetZenith):
        """Return a datetime of an offset by degrees below or above the horizon of sunrise.
        
        Arguments:
        offsetZenith -- the degrees before getSunrise() to use in the calculation. For time 
        after sunrise use negative numbers. Note that the degree offset is from the vertical, so
        for a calculation of 14 deg before sunrise, an offset of 14 + self.GEOMETRIC_ZENITH = 104
        would have to be passed as a parameter.
        """
        dawn = self.getUTCSunrise(offsetZenith)
        if not dawn:
            return None
        return self.getDateFromTime(dawn)

    def getSunsetOffsetByDegrees(self, offsetZenith):
        """Return a datetime of an offset by degrees below or above the horizon of sunset.
        
        Arguments:
        offsetZenith -- the degrees before getSunset() to use in the calculation. For time 
        after sunrise use negative numbers. Note that the degree offset is from the vertical, so
        for a calculation of 14 deg before sunset, an offset of 14 + self.GEOMETRIC_ZENITH = 104
        would have to be passed as a parameter.If the calculation can't be computed such as in the
        Arctic Circle where there is at least one day a year where the sun does not rise, and one
        where it does not set, None will be returned.
        """
        sunset = self.getUTCSunset(offsetZenith)
        if not sunset:
            return None
        else:
            return self.getAdjustedSunsetDate(self.getDateFromTime(sunset), self.getSunriseOffsetByDegrees(offsetZenith))

    def __init__(self, geoLocation=GeoLocation(), dt=None):
        """Initialise the Class - geolocation and datetime as parameters (Defaults to Greenwich and current system time)"""
        if not dt:
            self._dt = datetime.now(tz=geoLocation.timeZone)
        else:
            self._dt = dt.replace(tzinfo=geoLocation.timeZone)
        self._geolocation = geoLocation  # duplicate call
        self.astronomical_calculator = SunTimesCalculator()

    def getUTCSunrise(self, zenith):
        """Return the sunrise in UTC time without correction for time zone offset from GMT and
        without using daylight savings time.

        Arguments:
        zenith -- the degrees below the horizon. For time after sunrise use negative numbers

        Returns the time in the format: 18.75 for 18:45:00 UTC/GMT.
        When there is no sunrise None will be returned
        """
        return self.astronomical_calculator.getUTCSunrise(self.dt, self.geolocation, zenith, True)

    def getUTCSeaLevelSunrise(self, zenith):
        """Same as getUTCSunrise() but without taking into account elevation"""
        return self.astronomical_calculator.getUTCSunrise(self.dt, self.geolocation, zenith, False)

    def getUTCSunset(self, zenith):
        """Return the sunset in UTC time without correction for time zone offset from GMT and without using
        daylight savings time.

        Arguments:
        zenith -- the degrees below the horizon. For time after sunset use negative numbers

        Returns the time in the format: 18.75 for 18:45:00 UTC/GMT.
        When there is no sunset None will be returned
        """
        return self.astronomical_calculator.getUTCSunset(self.dt, self.geolocation, zenith, True)

    def getUTCSeaLevelSunset(self, zenith):
        """Same as getUTCSunset() but without taking into account elevation"""
        return self.astronomical_calculator.getUTCSunset(self.dt, self.geolocation, zenith, False)

    def getTemporalHour(self, startOfday=None, endOfDay=None):
        """Return length of a Shaa zmanis as timedelta (solar Hour - time between beginning and end of the day /12)
        
        Arguments:
        startOfday -- The start of the day.
        endOfDay -- The end of the day.
        If there is no start or end of Day (eg in Arctic circle) returns None
        """
        if not startOfday:
            startOfday = self.getSeaLevelSunrise()
        if not endOfDay:
            endOfDay = self.getSeaLevelSunset()
        if ((not startOfday) or (not endOfDay)):
            return None
        return (endOfDay - startOfday) / 12

    def getSunTransit(self, startOfDay = None, endOfDay = None):
        """A method that returns sundial or solar noon. It occurs when the Sun is <a href
        ="http://en.wikipedia.org/wiki/Transit_%28astronomy%29">transitting</a> the <a
        href="http://en.wikipedia.org/wiki/Meridian_%28astronomy%29">celestial meridian</a>. In this class it is
        calculated as halfway between the sunrise and sunset passed to this method. This time can be slightly off the
        real transit time due to changes in declination (the lengthening or shortening day).
        
        Arguments:
        startOfday -- The start of the day.
        endOfDay -- The end of the day.
        If there is no start or end of Day (eg in Arctic circle) returns None
        """
        if not startOfDay and not endOfDay:
            startOfDay = self.getSeaLevelSunrise()
            endOfDay = self.getSeaLevelSunset()
        if not startOfDay or not endOfDay:
            return None
        return startOfDay + (self.getTemporalHour(startOfDay, endOfDay) * 6)

    def getDateFromTime(self, hours):
        """Return timezone aware datetime from the UTC time passed in.
        Argument:
        hours -- The time expected is in base 10 decimal format: 18.75 for 6:45:00 PM.
        """
        if not hours:
            return None
        #more work here
        dt = datetime(self.dt.year, self.dt.month, self.dt.day, tzinfo=timezone('UTC'))
        gmtOffset = self.dt.tzinfo.utcoffset(self.dt).total_seconds() / 3600 # raw non DST offset
        # Set the correct calendar date in UTC. For example Tokyo is 9 hours ahead of GMT. Sunrise at ~6 AM will be at
        # ~21 hours GMT of the previous day and has to be set accordingly. In the case of California USA that is 7
        # hours behind GMT, sunset at ~6 PM will be at ~1 GMT the following day and has to be set accordingly.
        if (hours + gmtOffset > 24):
            dt -= timedelta(days=1)
        elif (hours + gmtOffset < 0):
            dt += timedelta(days=1)
        dt += timedelta(hours=hours)
        return dt.astimezone(self.dt.tzinfo)

    def getSunriseSolarDipFromOffset(self, minutes):
        """Returns the dip in degrees below the horizon befor sunrise that matches the offset minutes 
        passed in as a parameter. For example passing in 72 minutes for a calendar set to the equinox
        in Jerusalem returns a value close to 16.1 deg

        Please note that this method is very slow and inefficient and should NEVER be used in a loop.
        TODO: Improve efficiency.
        """
        offsetByDegrees = self.getSeaLevelSunrise()
        offsetByTime = self.getSeaLevelSunrise() - timedelta(minutes=minutes)

        degrees = 0
        incrementor = 0.0001
        while (offsetByDegrees == None or offsetByDegrees.getTime() > offsetByTime.getTime()):
            degrees += incrementor
            offsetByDegrees = self.getSunriseOffsetByDegrees(self.GEOMETRIC_ZENITH + degrees*2)
    
        return degrees*2

    def getSunsetSolarDipFromOffset(self, minutes):
        """Returns the dip in degrees below the horizon after sunset that matches the offset minutes 
        passed in as a parameter. For example passing in 72 minutes for a calendar set to the equinox
        in Jerusalem returns a value close to 16.1 deg

        Please note that this method is very slow and inefficient and should NEVER be used in a loop.
        TODO: Improve efficiency.
        """
        offsetByDegrees = self.getSeaLevelSunset()
        self.offsetByTime = self.getSeaLevelSunrise() + timedelta(minutes=minutes)
        degrees = 0
        incrementor = 0.0001
        while (offsetByDegrees == None or offsetByDegrees.getTime() < offsetByTime.getTime()):
            degrees += incrementor
            offsetByDegrees = self.getSunsetOffsetByDegrees(self.GEOMETRIC_ZENITH + degrees*2)
        return degrees*2

    @property
    def geolocation(self):
        """ The location"""
        return self._geolocation

    @geolocation.setter
    def geolocation(self, geolocation):
        """ The location"""
        self._geolocation = geoLocation
        self.dt.replace(tzinfo=geoLocation.timeZone)

    @property
    def dt(self):
        """ The datetime of the class"""
        return self._dt

    @dt.setter
    def dt(self, dt):
        """ The datetime of the class"""
        if self.geolocation: # if available set the datetime's timezone to the GeoLocation TimeZone
            self._dt = dt.replace(tzinfo=self.geolocation.timeZone)
        else:
            self.dt = dt
            self._sunrise = None
            self._sunset = None


class ZmanimCalendar(AstronomicalCalendar):
    """The ZmanimCalendar is a specialized calendar that can calculate sunrise and sunset and Jewish zmanim
    (religious times) for prayers and other Jewish religious duties. This class contains the main functionality of the
    Zmanim library. For a much more extensive list of zmanim use the ComplexZmanimCalendar that extends this
    class.
    Note: It is important to read the technical notes on top of the AstronomicalCalculator documentation.
    Disclaimer: I did my best to get accurate results but please do not rely on these zmanim for halacha lemaaseh.
    Author: Eliyahu Hershfeld 2004 - 2013
    """

    GEOMETRIC_ZENITH = AstronomicalCalendar.GEOMETRIC_ZENITH
    """The zenith of 16.1 deg below geometric zenith (90 deg). This calculation is used for determining alos
    (dawn) and tzais (nightfall) in some opinions. It is based on the calculation that the time between dawn
    and sunrise (and sunset to nightfall) is 72 minutes, the time that is takes to walk 4 mil at 18 minutes
    a mil (Rambam and others). The sun's position at 72 minutes before sunrise in Jerusalem on the equinox is
    16.1 deg below geometric zenith}.
    """
    ZENITH_16_POINT_1 = GEOMETRIC_ZENITH + 16.1

    """The zenith of 8.5 deg below geometric zenith (90 deg). This calculation is used for calculating alos
    (dawn) and tzais (nightfall) in some opinions. This calculation is based on the position of the sun 36
    minutes after sunset in Jerusalem on March 16, about 4 days before the equinox, the day that a
    solar hour is 60 minutes, which is 8.5 deg below geometric zenith. The Ohr Meir considers this the time
    that 3 small stars are visible, which is later than the required 3 medium stars.
    """
    ZENITH_8_POINT_5 = GEOMETRIC_ZENITH + 8.5
    candle_lighting_offset = 18  # in Jerusalem 40 and some use 15

    def getTzais(self):
        """Returns tzais (nightfall) when the sun is 8.5 deg below western geometric horizon.
        See ZENITH_8_POINT_5 for mor info
        """ 
        return self.getSunsetOffsetByDegrees(self.ZENITH_8_POINT_5)

    def getAlosHashachar(self):
        """Returns Alos (dawn) based on sun being 16.1 deg below the horizon. See ZENITH_16_POINT_1 for more info"""
        return self.getSunriseOffsetByDegrees(self.ZENITH_16_POINT_1)

    def getAlos72(self):
        """Return datetime of alos (dawn) calculated using 72 minutes before sea level sunrise
        Based on the time to walk the distance of 4 Mil at 18 minutes a Mil . This is based on the opinion of
        most Rishonim who stated that the time of the Neshef (time between dawn and sunrise) does not vary by
        the time of year or location but purely depends on the time it takes to walk the distance of 4 Mil.
        """ 
        return self.getSeaLevelSunrise() - timedelta(minutes=72)

    def getChatzos(self):
        """Return datetime of chatzos (midday) following the opinion of the GRA that the day for Jewish halachic
        times start at sea level sunrise and ends atsea level sunset
        """
        return self.getSunTransit()

    def getSofZmanShma(self, startOfDay, endOfDay):
        """Generic Sof Zman Shma function - takes the input start and end of day and returns a datetime from that"""
        shaahZmanis = self.getTemporalHour(startOfDay, endOfDay)
        return startOfDay + shaahZmanis * 3

    def getSofZmanShmaGRA(self):
        """Return the latest time for Shma acc to the GRA and Bal Hatanya that the day goes from sunrise to sunset"""
        return self.getSofZmanShma(self.getSeaLevelSunrise(), self.getSeaLevelSunset())

    def getSofZmanShmaMGA(self):
        """Return the latest time for Shma acc to MGA that the day goes from dawn to to nightfall"""
        return self.getSofZmanShma(self.getAlos72(), self.getTzais72())

    def getTzais72(self):
        """Return tzais according to Rambam and Rabenu Tam that it is 72 minutes after sunset"""
        return self.getSeaLevelSunset() + timedelta(minutes=72)

    def getCandleLighting(self):
        """Return Candle lighting time according to self.candle_lighting_offset"""
        return self.getSeaLevelSunset() - timedelta(minutes=self.candle_lighting_offset)

    def getSofZmanTfila(self, startOfDay, endOfDay):
        """Generic Sof Zman Tfila function - takes the input start and end of day and returns a datetime from that"""
        shaahZmanis = self.getTemporalHour(startOfDay, endOfDay)
        return startOfDay + (shaahZmanis * 4)

    def getSofZmanTfilaGRA(self):
        """Return the latest time for Tfila acc to the GRA and Bal Hatanya that the day goes from sunrise to sunset"""
        return self.getSofZmanTfila(self.getSeaLevelSunrise(), self.getSeaLevelSunset())

    def getSofZmanTfilaMGA(self):
        """Return the latest time for Tfila acc to the MGA that the day goes from dawn of 72 mins to to nigtfall of 72 mins"""
        return self.getSofZmanTfila(self.getAlos72(), self.getTzais72())

    def getMinchaGedola(self, startOfDay=None, endOfDay=None):
        """Return datetime of Mincha Gedola calculated as 6.5 shaah zmanis hours after sunrise.
        Default follows the opinion of the GRA and Bal Hatanya that shaa zmanis is from sunrise to sunset
        Any start of day and end of day can be passed in though
        """
        if not startOfDay:
            startOfDay = self.getSeaLevelSunrise()
        if not endOfDay:
            endOfDay = self.getSeaLevelSunset()
        shaahZmanis = self.getTemporalHour(startOfDay, endOfDay)
        return startOfDay + (shaahZmanis * 6.5)

    def getMinchaKetana(self, startOfDay=None, endOfDay=None):
        """Return datetime of Mincha Ketana calculated as 9.5 shaah zmanis hours after sunrise.
        Default follows the opinion of the GRA and Bal Hatanya that shaa zmanis is from sunrise to sunset
        Any start of day and end of day can be passed in though
        """
        if not startOfDay:
            startOfDay = self.getSeaLevelSunrise()
        if not endOfDay:
            endOfDay = self.getSeaLevelSunset()
        shaahZmanis = self.getTemporalHour(startOfDay, endOfDay)
        return startOfDay + (shaahZmanis * 9.5)

    def getPlagHamincha(self, startOfDay=None, endOfDay=None):
        """Return datetime of Plag Hamincha calculated as 10.75 shaah zmanis hours after sunrise.
        Default follows the opinion of the GRA and Bal Hatanya that shaa zmanis is from sunrise to sunset
        Any start of day and end of day can be passed in though
        """
        if not startOfDay:
            startOfDay = self.getSeaLevelSunrise()
        if not endOfDay:
            endOfDay = self.getSeaLevelSunset()
        shaahZmanis = self.getTemporalHour(startOfDay, endOfDay)
        return startOfDay + (shaahZmanis * 10.75)

    def getShaahZmanisGra(self):
        """Return a shaah zmanis as timedelta acc to GRA & Bal Hataya that goes from sunrise to sunset"""
        return self.getTemporalHour(self.getSeaLevelSunrise(), self.getSeaLevelSunset())

    def getShaahZmanisMGA(self):
        """Return a shaah zmanis as timedelta according to the MGA that goes from dawn to dusk (72 minutes
        before sunrise and 72 minutes after sunset)
        """
        return self.getTemporalHour(self.getAlos72(), self.getTzais72())

    def __init__(self, location=GeoLocation(), datetime=None):
        """Initialise the class - takes a Geolocation and Datetime as arguments"""
        super(ZmanimCalendar, self).__init__(location, datetime)
