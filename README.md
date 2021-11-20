# stop_signal_TMS_Aug2017 
Programme for a TMS-incorporated sequential stop-signal task to evaluate online visuo-motor dynamics, for my Honours (Final Year) research project. 
This study has been peer-reviewed and published in an international neuroscience journal [(Seet, Livesey & Harris, 2019)].

### System Architecture

<img src="https://github.com/manuelseet/stop_signal_TMS_Aug2017/blob/main/system%20architecture.png" alt="system architecture" height = 450/>
 
The research study required four system:
1)  A host computer with the control programe (PsychoPy in python), linked to a CRT monitor for research-precision visual stimuli display that will interface with the research subject. A standard keyboard received keypress inputs from the subject, to determine accuracy & reaction time w.r.t. to specific visual stimuli. 
2) A Transcranial Magnetic Stimulation (TMS; MagStim) system, receiving event triggers from the host computer via parallel port I/O, to ensure precise delivery of the TMS stimuli via the eletromagnetic coil positioned over the primary motor cortex (M1) of the subject. 
3) A data acquistion hardware device (PowerLab) that continuously recorded EMG signals from the subject's responding hand and streamed it to the data store computer. It received the relayed event triggers from the TMS system. 
4) A data store computer that received and stored the continuous data stream and event markers from the data acquisition device. It displayed the real-time data stream via LabChart, together with the series of event-segmented recordings for researcher inspection. 

### TMS Parallel Port I/O Evaluation
Calibrated and tested the precision and synchrony of the Parallel Port component for use by an external transcranial magnetic stimulation system that delivers event triggers, as well as the data acquisition hardware. The programme supporting this can be found [here]. 

## References
Seet, M. S., Livesey, E. J., & Harris, J. A. (2019). Associatively-mediated suppression of corticospinal excitability: A transcranial magnetic stimulation (TMS) study. Neuroscience, 416, 1-8. Link: https://www.sciencedirect.com/science/article/abs/pii/S0306452219305226

[here]: https://github.com/manuelseet/parallel_IO_testprog
[(Seet, Livesey & Harris, 2019)]: https://www.sciencedirect.com/science/article/abs/pii/S0306452219305226
