/* Project Rebuild offline coaching engine. A review is rebuilt from recorded facts on each render. */
'use strict';
const CoachKit=(()=>{
 const isDone=(s)=>s==='completed'||s==='partial';
 const isSkip=(s)=>['missed','skipped','skippedAdvance'].includes(s);
 const dateLocal=(d)=>String(d||'').slice(0,10);
 const average=a=>a.length?a.reduce((n,x)=>n+x,0)/a.length:null;
 const rounded=x=>Math.round(x*10)/10;
 function review(s){
  const days=s.days||[],now=s.today,week=days.filter(x=>x.date<=now).slice(-7),yesterday=days.find(x=>x.date===dateLocal(new Date(new Date(now+'T12:00:00').getTime()-86400000).toISOString()));
  const strengthScheduled=week.filter(r=>r.scheduledStrength).length,strengthCompleted=week.filter(r=>isDone(r.strengthStatus)).length;
  const explicitlySkipped=week.filter(r=>isSkip(r.strengthStatus)).length;
  const unlogged=week.filter(r=>r.scheduledStrength&&r.date<now&&r.strengthStatus==='unlogged').length;
  const cardioMinutes=week.reduce((n,r)=>n+(r.cardioMinutes||0),0),target=Number(s.profile?.weeklyCardioTarget)||90;
  const foodDays=week.filter(r=>r.foodEntries>0).length;
  const energy=week.map(r=>r.energy).filter(x=>x!==null&&x!==undefined);
  const pain=week.filter(r=>r.backPain>=4||r.shoulderPain>=4);
  const avgEnergy=average(energy);
  let priority,accountability;
  if(!strengthScheduled){priority='Your strength schedule is not established yet. Review your assessment.';accountability='Training goals cannot be evaluated without a scheduled program.';}
  else if(strengthCompleted<strengthScheduled){priority=`Strength: ${strengthCompleted} of ${strengthScheduled} scheduled sessions recorded this week.`;
   accountability=`You are below the planned strength count so far. ${explicitlySkipped?explicitlySkipped+' confirmed skipped. ':''}${unlogged?unlogged+' past scheduled session'+(unlogged===1?' is':'s are')+' unlogged—this is not proof you skipped. ':''}Check whether you trained and forgot to record it.`;}
  else{priority=`Strength: ${strengthCompleted} of ${strengthScheduled} scheduled sessions recorded. Maintain consistency.`;
   accountability=`Your logged strength work matches the current scheduled count. Keep recording actual sets and reps; attendance alone does not prove progression.`;}
  const cardioGap=Math.max(0,target-cardioMinutes);
  if(cardioGap>0)accountability+=` Cardio: ${cardioMinutes}/${target} minutes recorded over the past seven days; ${cardioGap} minutes below the weekly target.`;
  if(foodDays===0)accountability+=' No food entries in the last seven days, so calorie intake cannot be assessed.';
  else if(foodDays<5)accountability+=` Food was logged on ${foodDays}/7 days, which is not enough to confidently assess your usual intake.`;
  if(pain.length>=2)accountability+=' Repeated higher symptom scores were recorded; avoid painful movements and consider professional guidance.';
  let yesterdayText='No prior-day records are available.';
  if(yesterday){
   if(yesterday.scheduledStrength){
     yesterdayText=isDone(yesterday.strengthStatus)?'Your scheduled strength session was recorded as completed.':isSkip(yesterday.strengthStatus)?'You explicitly logged the scheduled workout as skipped.':yesterday.strengthStatus==='recovery'?'You logged recovery instead of the scheduled strength session.':'A strength session was scheduled but has no completion record. That is unconfirmed, not a verified skip.';
   }else yesterdayText='No strength session was scheduled.';
   yesterdayText+=' '+(yesterday.cardioMinutes>0?`${yesterday.cardioMinutes} cardio minutes recorded.`:yesterday.cardioPlanMinutes>0?'Planned cardio has no completion record.':'No scheduled cardio was required.');
   yesterdayText+=' '+(yesterday.foodEntries?`${yesterday.foodEntries} food item(s) logged.`:'No nutrition entries recorded.');
  }
  const last=s.lastVisit?new Date(s.lastVisit):null;
  let since='This is your first tracked login. Today’s records are ready for review.';
  if(last&&!Number.isNaN(last.getTime())){
    const date=dateLocal(s.lastVisit),delta=Math.max(0,new Date(s.sessionStarted||Date.now()).getTime()-last.getTime());
    if(delta<60*60*1000){since='Welcome back. Less than an hour since your last visit; your current record remains available.'}
    else{
      const changed=days.filter(d=>d.date>date&&d.date<=now);
      const newlyStrength=changed.filter(d=>isDone(d.strengthStatus)).length;
      const newlyFood=changed.reduce((n,d)=>n+(d.foodEntries||0),0);
      const newlyCardio=changed.reduce((n,d)=>n+(d.cardioMinutes||0),0);
      since=`Since your previous login (${Math.round(delta/3600000)} hours ago), ${newlyStrength} completed strength sessions, ${newlyCardio} cardio minutes, and ${newlyFood} food entries are recorded on subsequent dates. Same-day changes cannot be reliably isolated from date-only summaries.`;
    }
  }
  let nextAction='Open the workout checklist and complete today’s planned activity if your symptoms allow.';
  if(pain.length>=2||((week.at(-1)?.backPain||0)>=4)||((week.at(-1)?.shoulderPain||0)>=4))nextAction='Review today’s pain ratings. Do not push through worsening symptoms; use recovery or contact a clinician if needed.';
  else if(week.at(-1)?.scheduledStrength&&!isDone(week.at(-1)?.strengthStatus))nextAction='Complete today’s planned strength checklist if it is still scheduled and your symptoms allow.';
  else if(foodDays<5)nextAction='Log your next meal with a reasonable serving estimate. Partial nutrition logs cannot support honest calorie feedback.';
  else if(cardioGap>0)nextAction='Fit in an appropriate scheduled walk or elliptical session—no catch-up double workouts.';
  return {priority,accountability,yesterday:yesterdayText,sinceLastVisit:since,nextAction,strengthScheduled,strengthCompleted,explicitlySkipped,unlogged,cardioMinutes,cardioTarget:target,foodDays,avgEnergy:avgEnergy===null?null:rounded(avgEnergy)};
 }
 return {review};
})();
