import sherpa_onnx, subprocess, numpy as np, json, sys, re
d='sherpa-onnx-streaming-zipformer-en-2023-06-26/'
r=sherpa_onnx.OnlineRecognizer.from_transducer(tokens=d+'tokens.txt',encoder=d+'encoder-epoch-99-avg-1-chunk-16-left-128.int8.onnx',decoder=d+'decoder-epoch-99-avg-1-chunk-16-left-128.onnx',joiner=d+'joiner-epoch-99-avg-1-chunk-16-left-128.int8.onnx',num_threads=2,sample_rate=16000,feature_dim=80,decoding_method='greedy_search',provider='cpu')
raw=subprocess.run(['ffmpeg','-v','error','-i','../voice.mp3','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout
x=np.frombuffer(raw,np.float32)
s=r.create_stream(); s.accept_waveform(16000,x); s.accept_waveform(16000,np.zeros(16000,np.float32)); s.input_finished()
while r.is_ready(s): r.decode_stream(s)
res=r.get_result_all(s) if hasattr(r,'get_result_all') else r.get_result(s)
print(res.text if hasattr(res,'text') else res)
toks=res.tokens; ts=res.timestamps
json.dump({'text':res.text,'tokens':toks,'timestamps':[float(t) for t in ts]},open('asr.json','w'))
print(len(toks))
