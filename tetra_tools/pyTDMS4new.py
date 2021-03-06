"""


================================================================
                Standalone Python TDMS reader,
   (not using the NI libraries for they were Windows-specific)
================================================================


based on the format description on
http://zone.ni.com/devzone/cda/tut/p/id/5696



Floris van Vugt
IMMM Hannover
http://florisvanvugt.free.fr/


I am greatly indebted for insightful bug-corrections by:
ADAM REEVE
JUERGEN NEUBAUER, PH.D.

Thanks guys!


"""



# S. Klanke:
#  * Fixed a few print-statements and integer divisons for Python 3 compatibility
#  * Use arrays for drastic speed improvements


import struct
import os
import array
import sys




# Tells us whether we should really output messages about what
# we have read (clutters the output buffer though)
verbose = False


# store previous values for the raw data properties for when
# they are repeated
object_rawdata = {}


def byteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """

    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()

    return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()








tocProperties = {
    'kTocMetaData'         : (1<<1),
    'kTocRawData'          : (1<<3),
    'kTocDAQmxRawData'     : (1<<7),
    'kTocInterleavedData'  : (1<<5),
    'kTocBigEndian'        : (1<<6),
    'kTocNewObjList'       : (1<<2),
    }







tdsDataTypes = [
    'tdsTypeVoid',
    'tdsTypeI8',
    'tdsTypeI16',
    'tdsTypeI32',
    'tdsTypeI64',
    'tdsTypeU8',
    'tdsTypeU16',
    'tdsTypeU32',
    'tdsTypeU64',
    'tdsTypeSingleFloat',
    'tdsTypeDoubleFloat',
    'tdsTypeExtendedFloat',
    'tdsTypeSingleFloatWithUnit',
    'tdsTypeDoubleFloatWithUnit',
    'tdsTypeExtendedFloatWithUnit',
    'tdsTypeString',
    'tdsTypeBoolean',
    'tdsTypeTimeStamp',
    'tdsTypeDAQmxRawData',
]


tdsDataTypesDefined = {
    0x19: 'tdsTypeSingleFloatWithUnit',
    0x20: 'tdsTypeString',
    0x21: 'tdsTypeBoolean',
    0x44: 'tdsTypeTimeStamp',
    0xFFFFFFFF:'tdsTypeDAQmxRawData',
}


if sys.platform == 'linux2':
    tdsDataTypesTranscriptions = {
        'tdsTypeVoid'                  : 'b',
        'tdsTypeI8'                    : 'b',
        'tdsTypeI16'                   : 'h', # short: standard size: 2 bytes
        'tdsTypeI32'                   : 'l',
        'tdsTypeI64'                   : 'q',
        'tdsTypeU8'                    : 'B',
        'tdsTypeU16'                   : 'H', # unsigned short: 2 bytes
        'tdsTypeU32'                   : 'I',
        'tdsTypeU64'                   : 'Q',
        'tdsTypeSingleFloat'           : 'f',
        'tdsTypeDoubleFloat'           : 'd',
        'tdsTypeExtendedFloat'         : ' ', #NOT YET IMPLEMENTED
        'tdsTypeSingleFloatWithUnit'   : ' ', #NOT YET IMPLEMENTED
        'tdsTypeDoubleFloatWithUnit'   : ' ', #NOT YET IMPLEMENTED
        'tdsTypeExtendedFloatWithUnit' : ' ', #NOT YET IMPLEMENTED
        'tdsTypeString'                :' ', # SHOULD BE HANDLED SEPARATELY
        'tdsTypeBoolean'               :'b',
        'tdsTypeTimeStamp'             :' ', # SHOULD BE HANDLED SEPARATELY
        'tdsTypeDAQmxRawData'          : 'I',

    }
elif sys.platform == 'win32':
    tdsDataTypesTranscriptions = {
        'tdsTypeVoid'                  : 'b',
        'tdsTypeI8'                    : 'b',
        'tdsTypeI16'                   : 'h', # short: standard size: 2 bytes
        'tdsTypeI32'                   : 'l',
        'tdsTypeI64'                   : 'q',
        'tdsTypeU8'                    : 'B',
        'tdsTypeU16'                   : 'H', # unsigned short: 2 bytes
        'tdsTypeU32'                   : 'L',
        'tdsTypeU64'                   : 'Q',
        'tdsTypeSingleFloat'           : 'f',
        'tdsTypeDoubleFloat'           : 'd',
        'tdsTypeExtendedFloat'         : ' ', #NOT YET IMPLEMENTED
        'tdsTypeSingleFloatWithUnit'   : ' ', #NOT YET IMPLEMENTED
        'tdsTypeDoubleFloatWithUnit'   : ' ', #NOT YET IMPLEMENTED
        'tdsTypeExtendedFloatWithUnit' : ' ', #NOT YET IMPLEMENTED
        'tdsTypeString'                :' ', # SHOULD BE HANDLED SEPARATELY
        'tdsTypeBoolean'               :'b',
        'tdsTypeTimeStamp'             :' ', # SHOULD BE HANDLED SEPARATELY
        'tdsTypeDAQmxRawData'          : 'L',

    }
else:
    print 'unsupported os'





def dataTypeFrom( s ):
    """
    Find back the data type from
    raw input data.
    """
    repr = struct.unpack("<L", s)[0]
    if (repr in tdsDataTypesDefined.keys()):
        return tdsDataTypesDefined[repr]
    else:
        return tdsDataTypes[repr]



def dataTypeLength( datatype ):
    """
    How many bytes we need to read to
    read in an object of the given datatype
    """

    if (datatype in ['tdsTypeVoid']):
        return 1

    if (datatype in ['tdsTypeI8','tdsTypeU8','tdsTypeBoolean']):
        return 1

    if (datatype in ['tdsTypeI16','tdsTypeU16','tdsTypeDAQmxRawData',]):
        return 2

    if (datatype in ['tdsTypeI32','tdsTypeU32','tdsTypeSingleFloat','tdsTypeSingleFloatWithUnit',]):
        return 4

    if (datatype in ['tdsTypeI64','tdsTypeU64','tdsTypeDoubleFloat','tdsTypeDoubleFloatWithUnit']):
        return 8

    if (datatype in ['tdsTypeTimeStamp']):
        return 16


    if (datatype in [
            'tdsTypeString',
            'tdsTypeExtendedFloat',
            'tdsTypeExtendedFloatWithUnit',
            ]):
        return False






def dataTypeTranscription( datatype ):
    """
    Returns the identifier for the given datatype
    that we need to feed into struct.unpack to get
    the right thing out.
    """
    return tdsDataTypesTranscriptions[datatype]








def getValue( s, endianness, datatype ):
    """
    We just read s from the file,
    and now we need to unpack it.
    """
    if datatype=='tdsTypeTimeStamp':
        t = struct.unpack(endianness+"Qq", s)
        return (t[1],         # the number of seconds since the 1904 epoch
                t[0]*(2**-64) # plus the number of 2^-64 seconds
                )

    else:
        code = endianness+dataTypeTranscription(datatype)
        return struct.unpack(code, s)[0]

    return False






def readLeadIn( f ):
    """
    Read the lead-in of a segment
    """

    s = f.read(4) # read 4 bytes
    if (not s in [b'TDSm']):
        print ("Error: segment does not start with TDSm, but with ",s)
        exit()


    s = f.read(4)
    toc = struct.unpack("<i", s)[0]

    metadata = {}
    for prop in tocProperties.keys():
        metadata[prop] = (toc & tocProperties[prop])!=0

    # Contents type (bit mask not yet decoded)


    s = f.read(4)
    version = struct.unpack("<i", s)[0]


    s = f.read(16)
    (next_segment_offset,raw_data_offset) = struct.unpack("<QQ", s)
    return (metadata,version,next_segment_offset,raw_data_offset)



def readObject( f ):
    """
    Read object in the metadata array
    """

    # Read the object path
    s = f.read(4)
    lnth = struct.unpack("<L", s)[0]
    objectpath = f.read(lnth)

    s = f.read(4)
    rawdataindex = struct.unpack("<L", s)[0]


    # No raw data associated
    if   (rawdataindex==0xFFFFFFFF):
        rawdata=()

    # Raw data index same as before
    elif (rawdataindex==0x00000000):
        rawdata = ()
    elif(rawdataindex==0x00001269):

        # DataType
        s = f.read(4)
        rawdata_datatype = dataTypeFrom(s)

        # Dimension of the raw data array
        s = f.read(4)
        rawdata_dim = struct.unpack("<L", s)[0]

        # Number of raw data values
        s = f.read(8)
        rawdata_values = struct.unpack("<Q", s)[0]

        #Vector or Format Changing Scalers

        #Vector size
        s=f.read(4)
        if sys.platform == 'linux2':
            vector_size=struct.unpack("I",s)[0]
        elif sys.platform == 'win32':
            vector_size=struct.unpack("L",s)[0]


        #DAQmx data type
        s=f.read(4)
        if sys.platform == 'linux2':
            DAQmx_datatype=struct.unpack("I",s)[0]
        elif sys.platform == 'win32':
            DAQmx_datatype=struct.unpack("L",s)[0]
        if (DAQmx_datatype==3):
            rawdata_datatype="tdsTypeI16"
        elif (DAQmx_datatype==4):
            rawdata_datatype="tdsTypeU32"

        #Raw buffer index
        s=f.read(4)

        if sys.platform == 'linux2':
            Raw_buffer_index=struct.unpack("I",s)[0]
        elif sys.platform == 'win32':
            Raw_buffer_index=struct.unpack("L",s)[0]

        #Raw byte offset within stride
        s=f.read(4)
        if sys.platform == 'linux2':
            byte_offset=struct.unpack("I",s)[0]
        elif sys.platform == 'win32':
            byte_offset=struct.unpack("L",s)[0]

        #Sample format bitmap
        s=f.read(4)
        if sys.platform == 'linux2':
            format_bitmap=struct.unpack("I",s)[0]
        elif sys.platform == 'win32':
            format_bitmap=struct.unpack("L",s)[0]

        #Scale ID
        s=f.read(4)
        if sys.platform == 'linux2':
            scale_id=struct.unpack("I",s)[0]
        elif sys.platform == 'win32':
            scale_id=struct.unpack("L",s)[0]

        #Size of vector of raw data width
        s=f.read(4)
        if sys.platform == 'linux2':
            vector_width=struct.unpack("I",s)[0]
        elif sys.platform == 'win32':
            vector_width=struct.unpack("L",s)[0]

        #first element
        s=f.read(4)
        if sys.platform == 'linux2':
            element=struct.unpack("I",s)[0]
        elif sys.platform == 'win32':
            element=struct.unpack("L",s)[0]

        rawdata=(
            rawdata_datatype,
            rawdata_dim,
            rawdata_values,
            )
        object_rawdata[objectpath] = rawdata



    else:

        #print ("==>Raw data reading",byteToHex(s),",that is,",rawdataindex,"bytes")

        # New raw data index!

        inf_length = rawdataindex


        # DataType
        s = f.read(4)
        rawdata_datatype = dataTypeFrom(s)

        # Dimension of the raw data array
        s = f.read(4)
        rawdata_dim = struct.unpack("<L", s)[0]

        # Number of raw data values
        s = f.read(8)
        rawdata_values = struct.unpack("<Q", s)[0]

        rawdata=(
            rawdata_datatype,
            rawdata_dim,
            rawdata_values
            )
        object_rawdata[objectpath] = rawdata

        #print "==>Done reading raw data:",rawdata

        
        
        
    # Read the number of properties
    s = f.read(4)
    nProp = struct.unpack("<L", s)[0]
    
    #print ("Has",nProp,"properties")

    properties = {}
    for j in range(0,nProp):
        
        # Read one property
        
        # Read the property name
        s = f.read(4)
        numb = struct.unpack("<L", s)[0]
        name = f.read(numb)
        
        
        # Read the data type
        s = f.read(4)
       
        datatype = dataTypeFrom(s)

        value = ''

        # If it's a string, read the length
        if (datatype=='tdsTypeString'):
            s = f.read(4)
            lengte = struct.unpack("<L", s)[0]
            value = f.read(lengte)
         
            
        else:            
            nm = dataTypeLength( datatype )
            s = f.read(nm)
            value = getValue( s, "<", datatype )
            
        properties[name]=(datatype,value)

    return (objectpath,
            rawdataindex,
            rawdata,
            properties)






def mergeProperties( prop, newprop ):
    """
    Merge the two property lists, using the newprop
    list to overwrite if conflicts arise.
    """
    
    # What we will return
    retprop = prop

    # Now we change the values wherever we need to
    for k in newprop.keys():
        retprop[k]=newprop[k]

    # And the return the merged list
    return retprop





def mergeObject( obj, newobj ):
    """
    Ok, we are given two objects: obj and alt.
    We make all the changes (new values or
    overwriting old values), taking newobj as
    dominant.
    """

    (objectpath,
     rawdataindex,
     rawdata,
     properties) = obj

    (newobjectpath,
     newrawdataindex,
     newrawdata,
     newproperties) = newobj


    # We assume that objectpath is the same
    if (newobjectpath!=objectpath):
        print("Error: trying to merge non-same objectpaths:",newobjectpath,objectpath)
        exit()


    # If there is some change in the raw data associated
    if (not (newrawdataindex in [0xFFFFFFFF,0x00000000])):
        retrawdataindex = newrawdataindex
        retrawdata      = newrawdata
    else:
        retrawdataindex = rawdataindex
        retrawdata      = rawdata

    return (objectpath,
            retrawdataindex,
            retrawdata,
            mergeProperties(properties,newproperties))

    



def mergeObjects( objects, newobjects ):
    """
    Return the objects (metadata), but
    add the stuff that is in newobjects.
    """
    retobjects = objects

    # For all the new objects...
    for obj in newobjects.keys():
        ##print("for ", obj,"in ", newobjects.keys())

        # See if there is an old version already
        if (obj in retobjects.keys()):
            # Then update the old version using the new information
            retobjects[obj] = mergeObject(retobjects[obj],newobjects[obj])
        else:

            # Else just add it anew
            retobjects[obj] = newobjects[obj]
    
    return retobjects








def readMetaData( f ):
    """
    Read meta data from file f.
    
    We return (objects,objectorder) where
    objects is the structure containing all information about
    objects, and objectorder is a list of objectpaths (object ID's if you want)
    in the order that they have been presented. We need this
    later when we start reading the raw data, since it then comes
    in this very order.
    """

    # The number of objects in this metadata
    s = f.read(4)
    nObjects = struct.unpack("<l", s)[0]
    objects     = {}
    objectorder = []
    for i in range(0,nObjects):
        obj = readObject(f)
        (objectpath,
         rawdataindex,
         rawdata,
         properties) = obj

        if verbose:
            print("Read object",objectpath)
        # Add this object, or, if an object with the same objectpath
        # exists already, make it update that one.
        if (objectpath in objects.keys()):
            objects[objectpath] = mergeObjects(objects[objectpath],obj)
        else:
            # We add it anew
            objects[objectpath] = obj
            objectorder.append( objectpath )

    return (objects,objectorder)





def isChannel(obj):
    """
    Tell us whether the given object is a channel
    (in the current segment) and if so, returns
    the meta information about the raw data.
    """
    (_,rawdataindex,_,_) = obj
    return rawdataindex!=0xFFFFFFFF









def readRawData( f, leadin, segmentobjects, objectorder, filesize ):
    """
    Read raw data from file f,
    given the previously read leadin.
    segmentobjects are the objects that are given in this segment.
    Objectorder is a list of objectpaths (object id's) that shows
    the order in which the objects are given in the metadata. 
    That is important, for that will be the order in which their
    raw data needs to be read.
    """

    (metadata,version,next_segment_offset,raw_data_offset) = leadin

    # Whether the channel data is interleaved
    interleaved = metadata["kTocInterleavedData"]

    # Set the correct endianness (still need to check this!)
    endianness = '<'
    if metadata['kTocBigEndian']: endianness = '>'



    # First see which objects are channels (or really
    # actually which objects are channels AND have data in this segment.
    channel_sizes = {}
    channels = [ obj for obj in objectorder if isChannel(segmentobjects[obj]) ]
    
    for c in channels:
        channel = segmentobjects[c]
        (name,rawdataindex,rawdata,values)=channel
        (rawdata_datatype, rawdata_dim, rawdata_values) = rawdata

        if (rawdata_dim!=1):
            print("Error! Raw data dimension is ",rawdata_dim," and should have been 1.")
            exit()
        
        # Calculate how many bytes a single value is
        datapointsize= dataTypeLength(rawdata_datatype)

        # Array dimension (should really be 1)
        channel_size = datapointsize * rawdata_dim * rawdata_values
        channel_sizes[c] = channel_size
        

        
    # How much data in all channels together
    chunk_size = sum([ channel_sizes[c] for c in channels ])

    # A correction given on the TDMS specification website
    if next_segment_offset==-1:
        next_segment_offset=filesize

    # Raw data size of total chunks
    # (next_segment_offset should already have been corrected if -1)
    total_chunks = next_segment_offset - raw_data_offset
    # Hm, I think this quantity should be the total data
    # in this segment.


    
    # Hack by dlr: handle cases where file reports that there's raw
    # data of size 0.
    if total_chunks == 0:
        n_chunks = 0
        chunk_size=0
    else:
        n_chunks = total_chunks // chunk_size
    
        if (total_chunks % chunk_size) != 0:
            raise ValueError("Data size is not a multiple of the chunk size")
    # end if...else, end of meddling by dlr.
    
    
    if verbose:
        print("Ready for reading",total_chunks,"bytes (",chunk_size, ") in",n_chunks,"chunks")

    
    # Initialise data to be empty
    data = {}
    for c in channels:
        (_, _, (datatype, _, _), values) = segmentobjects[c]
        data[c] = array.array(tdsDataTypesTranscriptions[datatype])
    if interleaved:
        if verbose:
            print(" ==> Interleaved")            
        
        j=0
        k=0
        
        if chunk_size>0:
            while j<chunk_size:
                for c in channels:
                    data[c].fromfile(f, 1)
                    j+=datapointsize
    else:
        if verbose:
            print(" ==> Not Interleaved")
         
        for chunk in range(n_chunks):
            for c in channels:
                size= channel_sizes[c]
                (name,
                 rawdataindex,
                 (datatype, rawdata_dim, rawdata_values),
                 values) = segmentobjects[c]
                 
                data[c].fromfile(f, rawdata_values)

    file10 = struct.unpack(endianness + 'h', b'\1\0')
    host10 = struct.unpack('=h', b'\1\0')
    
    if file10 != host10:
       for c in channels:
          data[c].byteswap() 
    return data









def mergeRawData( rawdata, newrawdata ):
    """
    Return the raw data, appended the new
    raw data.
    """
    for channel in newrawdata.keys():

        # If we already had data on this channel
        if (channel in rawdata.keys()):
            rawdata[channel].extend(newrawdata[channel])

        # Else we just chart it annew
        else:
            rawdata[channel] = newrawdata[channel]
    return rawdata

    







def readSegment( f, filesize, data ):
    """
    Read a segment from file f, whose filesize is given,
    and data is what we have read already
    """

    # This is the data we have so far.
    # The stuff in this segment is going to append to this.
    (objects,rawdata)=data
    

    leadin = readLeadIn(f)
    (metadata,version,next_segment_offset,raw_data_offset) = leadin
    next_segment_position=(f.tell()+next_segment_offset)
  
    newobjects = {}
    # If the segment has metadata...
    if (metadata["kTocMetaData"]):

        # Read the meta data
        (newobjects,newobjectorder) = readMetaData(f)
        # Merge the new information with what we knew already about the objects.
        objects = mergeObjects( objects, newobjects )



    if (metadata["kTocRawData"]):

        # Read the raw data
        newdata = readRawData(f,leadin,newobjects,newobjectorder,filesize)

        # And merge the data we just read with what we knew already
        rawdata = mergeRawData( rawdata, newdata )
    f.seek(next_segment_position,0)
    return (objects,rawdata)







def dumpProperties(props):
    ret = ''
    for pr in props:
        (tp,val)=props[pr]
        ret = ret + (pr+'=') + str(val) + ", "
    return ret



def csvDump(objects,data):
    """
    Dump the (objects,rawdata) that we read from a TDMS file
    straight into a CSV file.
    """

    ret = ''
    for obj in objects.keys():

        # Objects
        (objectpath,
         rawdataindex,
         rawdata,
         properties) = objects[obj]
        
        ##print ("OBJECT "+objectpath+" ("+dumpProperties(properties)+")\n")
        # ret = ret + ''

    i = 0
    maxi = max([ len(data[obj]) for obj in objects.keys() if obj in data.keys() ])

    channels = [ obj for obj in objects.keys() if isChannel(objects[obj]) ]
    ret += '\t'.join(str(channels))+'\n'

    for i in range(maxi):
        
        for obj in channels:

            val = ''
            if ((obj in data.keys()) and i<len(data[obj])):
                val = str(data[obj][i])
                # The raw data associated with the object
        
            ret += val+"\t"

        ret += "\n"

    return ret



def read( filename ):
    """
    Reads TDMS file with the given filename.
    We return the data, which is, object meta data and raw channel data.

    Notice that we do not read the (optionally) accompanying .tdms_index
    since it is supposed to be an exact copy of the .tdms file, without the
    raw data. So it should contain nothing new.
    """



    # We start with empty data
    data = ({},{})




    # Then we read the data from a file, and return that
    f = open(filename, "rb")  # Open in binary mode for portability
    sz = os.path.getsize(filename)
    
    # While there's still something left to read
    while f.tell()<sz:
        #print("Current Position: %d" % f.tell())
        #print("size=",sz)
        # Now we read segment by segment
        data = readSegment(f,sz,data)
    f.close()
    return data
 






