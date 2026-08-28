# Lottie Android Integration for Premium Motion Graphics

> Connected: https://github.com/airbnb/lottie-android (35.7k stars)
> Also: Lottie iOS, React Native, Web, Windows — https://airbnb.io/lottie/

Lottie is a mobile library that parses Adobe After Effects animations exported as JSON with Bodymovin and renders them natively!

For the first time, designers can create and ship beautiful animations without an engineer painstakingly recreating it by hand.

## Why Lottie for Finance-Australia 40+?

Beyond sliding images, we need premium motion graphics that resonate:

- **Money bag animation**: Coins dropping into super piggy bank with bounce
- **House SOLD**: House with SOLD stamp + confetti
- **Tax saving**: Calculator with numbers counting up, saving badge pop
- **Success state**: Checkmark draw + particle burst + green fill (from LottieFiles pattern)
- **Error shake**: For mistakes to avoid section
- **$600k couple**: Two figures high-five with heart

Lottie JSON files are small, vector, scalable, and work on Android, iOS, Web, React Native.

## Download

Gradle (Android):
```groovy
dependencies {
  implementation 'com.airbnb.android:lottie:$lottieVersion'
}
```

Latest version badge: https://maven-badges.herokuapp.com/maven-central/com.airbnb.android/lottie

Lottie-Compose (Jetpack Compose):
```groovy
implementation 'com.airbnb.android:lottie-compose:6.x.x'
```

## Usage

### Android View
```xml
<com.airbnb.lottie.LottieAnimationView
  android:id="@+id/animationView"
  android:layout_width="wrap_content"
  android:layout_height="wrap_content"
  app:lottie_rawRes="@raw/animation"
  app:lottie_autoPlay="true"
  app:lottie_loop="true" />
```

```java
LottieAnimationView animationView = findViewById(R.id.animationView);
animationView.playAnimation();
```

### Jetpack Compose
```kotlin
val composition by rememberLottieComposition(LottieCompositionSpec.RawRes(R.raw.animation))
val progress by animateLottieCompositionAsState(composition, iterations = LottieConstants.IterateForever)
LottieAnimation(composition, progress)
```

### Web (for Hyperframes HTML-to-video)
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
<div id="lottie"></div>
<script>
  lottie.loadAnimation({
    container: document.getElementById('lottie'),
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: 'animations/money-bag.json'
  });
</script>
```

## For Voicebox Premium Motion

We combine:
- LottieFiles motion-design-skill: principles (timing, easing, personality)
- Hyperframes: HTML-to-video pipeline with GSAP + Lottie support
- Lottie Android: native After Effects animations as JSON
- MemOS: remembers which Lottie works

Example: Downsizer house reveal with Lottie
- Primary: House SOLD Lottie animation (stamp + bounce)
- Secondary: Piggy bank coins dropping Lottie
- Ambient: Confetti Lottie particle burst
```

