# 81W — 30호 ANEM(2026-11-18): 판정 구성 대조 게이트 결과 판정/혈색소 비가 2013·2018에 계단 → 판정 안정 구간 재적합.
#  81_fit_inla.R 1~60행(설정·그래프·fitf) 그대로 실행 후 주모형(같은 변수·우도)을 2013-2017, 2018-2024, 2013-2024에 적합. 산출 results_std3/S4j_judgement_windows_IRR.csv
src<-readLines(file.path(dirname(sub("--file=","",grep("--file=",commandArgs(),value=TRUE))),"81_fit_inla.R"))[1:60]
eval(parse(text=src))
MI<-read.csv(file.path(RES,"S3_main_IRR.csv"),stringsAsFactors=FALSE);MAINV<-MI$cov;MAINFAM<-read.csv(file.path(RES,"S3_main_fit.csv"))$family[1]
W<-list(J2_2013_17=c(2013,2017),J3_2018_24=c(2018,2024),J23_2013_24=c(2013,2024))
out<-NULL;fo<-NULL
for(wn in names(W)){yy<-W[[wn]];d<-DD[DD$year>=yy[1]&DD$year<=yy[2],];d$time<-d$year-min(d$year)+1;d$yiid<-d$time;d$id<-seq_len(nrow(d))
  m<-timed(wn,safefit(MAINV,MAINFAM,data=d,cpo=FALSE));if(is.null(m))next
  r<-do.call(rbind,lapply(MAINV,function(v)irr(m,v)));r$window<-wn;r$years<-sprintf("%d-%d",yy[1],yy[2]);r$n_obs<-nrow(d);r$WAIC<-round(m$waic$waic,1);out<-rbind(out,r)}
write.csv(out,file.path(RES,"S4j_judgement_windows_IRR.csv"),row.names=FALSE);LOG("done")
