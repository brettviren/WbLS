void stats(const char* from, const char* to)
{
    gROOT->Reset();
    TString prefix = ".";
    TString include = ".include ";
    TString load = ".L ";

    gROOT->ProcessLine( include + prefix );
    gROOT->ProcessLine( load + prefix + "/CEventStats.cc+" );

    CEventStats ev(from, to);
    ev.Loop();

}