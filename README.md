🍽️ Smart Restaurant Ordering & Sentiment Analysis System

A Smart Restaurant Web Application built using Django, HTML, CSS, and JavaScript that enables customers to place food orders, specify allergy information,Recurrent Neural Network (RNN) for customer sentiment analysis, and provide feedback, while allowing admins and kitchen staff to manage orders efficiently through a custom admin dashboard and Kitchen Display System (KDS) with sentiment analysis support.


📌 Key Highlights

✔ RNN-based sentiment analysis
✔ Custom admin dashboard (not Django default)
✔ Kitchen Display System (KDS)
✔ Allergy-aware food ordering
✔ Dynamic JavaScript menu rendering
✔ Academic + real-world project design

📌 Features
👤 Customer Side

 *Dynamic food ordering using JavaScript const menu
 *Displays all food items without hardcoding in HTML
 *Quantity selection for each food item
 *Allergy input field (optional)      “Are you allergic to any ingredients?”
 *Consistent food pricing across menu, order, admin, and KDS
 *Feedback submission after order completion(use RNN ko analysized sentiment)

🔐 Custom Admin Panel 

  *Custom admin login & logout
   *Role-based access 
   *Dashboard with:
     *Total orders
      *Pending orders
      *Delayed orders
       *Ready orders
   *Order management with time tracking
   *Allergy alert visibility
   *Feedback & sentiment overview

👨‍🍳 Kitchen Display System (KDS)

  *Real-time display of customer orders
   *Card-based UI for kitchen staff
    
**Shows:

*Order ID
*Table number
*Food items & quantities
*Time elapsed
*Allergy alerts (highlighted)
*Order status controls:
*Start Cooking
*Mark Ready
*FIFO order handling

*Delayed order highlighting

💬 Feedback & Sentiment Analysis

*Customer feedback linked to orders

*Sentiment classification:

   *Positive
    *Neutral
    *Negative
    *Emotion tagging

*Helps improve service quality
