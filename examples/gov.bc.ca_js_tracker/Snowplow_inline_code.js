// <!-- Snowplow starts plowing -->
//  <script type="text/javascript">
;(function(p,l,o,w,i,n,g){if(!p[i]){p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];
 p.GlobalSnowplowNamespace.push(i);p[i]=function(){(p[i].q=p[i].q||[]).push(arguments)
 };p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];n.async=1;
 n.src=w;g.parentNode.insertBefore(n,g)}}(window,document,"script","https://sp-js.apps.gov.bc.ca/kFaRq7wlqn92HjDbMi45LjA.js  ","snowplow"));
var collector = 'spm.gov.bc.ca';
 window.snowplow('newTracker','rt',collector, {
  appId: "",
  platform: 'web',
  respectDoNotTrack: true,
  post: true,
  forceSecureTracker: true,
  contexts: {
   webPage: true,
   performanceTiming: true
  }
 });
 window.snowplow('enableActivityTracking', 30, 30); // Ping every 30 seconds after 30 seconds
 window.snowplow('enableLinkClickTracking');
 window.snowplow('trackPageView');
//  </script>
//  <!-- Snowplow stop plowing -->
