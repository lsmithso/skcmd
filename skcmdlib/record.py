import sys, os, subprocess,  re, datetime
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
GObject.threads_init()
Gst.init(None)


class PulseAudioDefaults(object):
    def __init__(self):
        self.default_sink_name = None
        self.default_sink = 2
        self.default_source_name = None
        self.default_source = 3
        cmd = 'pactl info'
        p = subprocess.Popen(cmd.split(), stdin=None, stdout=subprocess.PIPE, stderr=sys.stderr)
        for l in  p.stdout.readlines():
            match = re.search(r'Default Sink: (.*)', l)
            if match:
                self.default_sink_name = match.group(1)
            match = re.search(r'Default Source: (.*)', l)
            if match:
                self.default_source_name = match.group(1)
            if self.default_sink_name and self.default_source_name:
                break
        if self.default_sink_name:
            self.default_sink = self.get_ssid(self.default_sink_name + '.monitor')
        if self.default_source_name:
            self.default_source = self.get_ssid(self.default_source_name)

    def  get_ssid(self, device_name):
        cmd = 'pactl list sources short' 
        p = subprocess.Popen(cmd.split(), stdin=None, stdout=subprocess.PIPE, stderr=sys.stderr)
        for l in  p.stdout.readlines():
            tid, tdn = l.split()[:2]
            if  tdn ==  device_name:
                return tid

                
    def __str__(self):
        return 'Default sink: %s/%s Default Source: %s/%s' % (self.default_sink, self.default_sink_name, self.default_source, self.default_source_name)
            


        
class  Record(object):

    RECORDING_DIR = os.path.expanduser('~/skcmd_recordings')

    def build_pipeline(self):
        pad = PulseAudioDefaults()
        pipe_template = 'pulsesrc device=%s ! adder name=mix ! audioconvert ! vorbisenc ! oggmux  ! filesink location=%s pulsesrc device=%s ! queue ! mix.'
        pipeline = pipe_template % (pad.default_sink, self.make_filename(), pad.default_source)
        print 'pipeline', pipeline
        self.pipeline =  Gst.parse_launch(pipeline)



    def start(self, filename_base):
        self.filename_base = filename_base
        self.build_pipeline()
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
            
    def make_filename(self):
        if not os.path.exists(self.RECORDING_DIR):
            os.mkdir(self.RECORDING_DIR)
        filename_base = self.filename_base.replace(' ', '')
        for i in range(1000):
            filename = os.path.join(self.RECORDING_DIR, '%s_%04d.ogg' % (filename_base, i))
            if not os.path.exists(filename):
                return filename
        raise RuntimeError('You have way too many recordings for %s' % filename_base)
        

if __name__ == '__main__':
    pad = PulseAudioDefaults()
    print pad
    
