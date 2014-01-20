import sys, os, subprocess, pygst, re, datetime
import pygst
pygst.require("0.10")
import gst

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

    def __str__(self):
        return 'Default sink: %s Default Source: %s' % (self.default_sink, self.default_source)
            


        
class  Record(object):

    RECORDING_DIR = os.path.expanduser('~/skcmd_recordings')

    def build_pipeline(self):
        pad = PulseAudioDefaults()
        pipe_template = 'pulsesrc device=%s ! adder name=mix ! audioconvert ! vorbisenc ! oggmux  ! filesink location=%s pulsesrc device=%s ! queue ! mix.'
        pipeline = pipe_template % (pad.default_sink, self.make_filename(), pad.default_source)
        print pipeline
        self.pipeline =  gst.parse_launch(pipeline)



    def start(self, filename_base):
        self.filename_base = filename_base
        self.build_pipeline()
        self.pipeline.set_state(gst.STATE_PLAYING)

    def stop(self):
        self.pipeline.set_state(gst.STATE_NULL)
            
    def make_filename(self):
        # TODO: remove whitespace from file basename
        if not os.path.exists(self.RECORDING_DIR):
            os.mkdir(self.RECORDING_DIR)
        
        now = datetime.datetime.now()
        filename = '%s_%s.ogg' % (self.filename_base, now.strftime('%Y%m%d%H%M%S'))
        return os.path.join(self.RECORDING_DIR, filename)
        

if __name__ == '__main__':
    pad = PulseAudioDefaults()
    print pad
    
